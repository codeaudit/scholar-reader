import os.path
from dataclasses import dataclass
from typing import Iterable, Iterator

from command.command import ArxivBatchCommand
from common import directories, file_utils
from common.match_symbols import get_mathml_matches
from common.types import ArxivId, Matches, MathML


@dataclass(frozen=True)
class MathMLForPaper:
    arxiv_id: ArxivId
    mathml_equations: Iterable[MathML]


class FindSymbolMatches(ArxivBatchCommand[MathMLForPaper, Matches]):
    @staticmethod
    def get_name() -> str:
        return "find-symbol-matches"

    @staticmethod
    def get_description() -> str:
        return "Find matches between a symbol and all other symbols in each paper."

    @staticmethod
    def get_entity_type() -> str:
        return "symbols"

    def get_arxiv_ids_dirkey(self) -> str:
        return "symbols"

    def load(self) -> Iterator[MathMLForPaper]:

        for arxiv_id in self.arxiv_ids:

            output_dir = directories.arxiv_subdir("symbol-matches", arxiv_id)
            file_utils.clean_directory(output_dir)

            symbols_with_ids = file_utils.load_symbols(arxiv_id)
            if symbols_with_ids is None:
                continue

            symbols_mathml = {swi.symbol.mathml for swi in symbols_with_ids}

            yield MathMLForPaper(arxiv_id=arxiv_id, mathml_equations=symbols_mathml)

    def process(self, item: MathMLForPaper) -> Iterator[Matches]:
        matches = get_mathml_matches(item.mathml_equations)
        yield matches

    def save(self, item: MathMLForPaper, result: Matches) -> None:
        output_dir = directories.arxiv_subdir("symbol-matches", item.arxiv_id)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        matches_path = os.path.join(output_dir, "matches.csv")
        for matches in result.values():
            for match in matches:
                file_utils.append_to_csv(matches_path, match)
