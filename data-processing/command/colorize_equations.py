import csv
import logging
import os.path
from argparse import ArgumentParser
from typing import Iterator, List, NamedTuple

from command.command import ArxivBatchCommand, add_one_entity_at_a_time_arg
from common import directories
from common.colorize_tex import ColorizedEntity, colorize_equations
from common.file_utils import clean_directory, find_files, read_file_tolerant
from common.types import ArxivId, FileContents, RelativePath
from common.unpack import unpack


class ColorizationTask(NamedTuple):
    arxiv_id: ArxivId
    tex_path: RelativePath
    file_contents: FileContents


class ColorizationResult(NamedTuple):
    iteration: int
    tex: str
    colorized_equations: List[ColorizedEntity]


class ColorizeEquations(ArxivBatchCommand[ColorizationTask, ColorizationResult]):
    @staticmethod
    def init_parser(parser: ArgumentParser) -> None:
        super(ColorizeEquations, ColorizeEquations).init_parser(parser)
        add_one_entity_at_a_time_arg(parser)

    @staticmethod
    def get_name() -> str:
        return "colorize-equations"

    @staticmethod
    def get_description() -> str:
        return "Instrument TeX to colorize equations."

    @staticmethod
    def get_entity_type() -> str:
        return "symbols"

    def get_arxiv_ids_dirkey(self) -> str:
        return "sources"

    def load(self) -> Iterator[ColorizationTask]:
        for arxiv_id in self.arxiv_ids:

            output_root = directories.arxiv_subdir(
                "sources-with-colorized-equations", arxiv_id
            )
            clean_directory(output_root)

            original_sources_path = directories.arxiv_subdir("sources", arxiv_id)
            for tex_path in find_files(original_sources_path, [".tex"], relative=True):
                file_contents = read_file_tolerant(
                    os.path.join(original_sources_path, tex_path)
                )
                if file_contents is not None:
                    yield ColorizationTask(arxiv_id, tex_path, file_contents)

    def process(self, item: ColorizationTask) -> Iterator[ColorizationResult]:
        batch_size = 1 if self.args.one_entity_at_a_time else None
        for i, batch in enumerate(
            colorize_equations(item.file_contents.contents, batch_size=batch_size)
        ):
            yield ColorizationResult(i, batch.tex, batch.entities)

    def save(self, item: ColorizationTask, result: ColorizationResult) -> None:
        iteration = result.iteration
        colorized_tex = result.tex
        colorized_equations = result.colorized_equations

        iteration_id = directories.tex_iteration(item.tex_path, str(iteration))
        output_sources_path = directories.iteration(
            "sources-with-colorized-equations", item.arxiv_id, iteration_id,
        )
        logging.debug("Outputting to %s", output_sources_path)

        # Create new directory for each colorization iteration for each TeX file.
        unpack_path = unpack(item.arxiv_id, output_sources_path)
        sources_unpacked = unpack_path is not None
        if unpack_path is None:
            logging.warning("Could not unpack sources into %s", output_sources_path)

        if sources_unpacked:
            tex_path = os.path.join(output_sources_path, item.tex_path)
            with open(tex_path, "w", encoding=item.file_contents.encoding) as tex_file:
                tex_file.write(colorized_tex)

            hues_path = os.path.join(output_sources_path, "equation_hues.csv")
            with open(hues_path, "a", encoding="utf-8") as hues_file:
                writer = csv.writer(hues_file, quoting=csv.QUOTE_ALL)
                for colorized_equation in colorized_equations:
                    try:
                        writer.writerow(
                            [
                                item.tex_path,
                                colorized_equation.identifier["index"],
                                iteration_id,
                                colorized_equation.hue,
                                colorized_equation.tex,
                                colorized_equation.data["content_start"],
                                colorized_equation.data["content_end"],
                                colorized_equation.data["content_tex"],
                                colorized_equation.data["depth"],
                                colorized_equation.data["start"],
                                colorized_equation.data["end"],
                            ]
                        )
                    except Exception:  # pylint: disable=broad-except
                        logging.warning(
                            "Couldn't write row for equation for arXiv %s: can't be converted to utf-8",
                            item.arxiv_id,
                        )