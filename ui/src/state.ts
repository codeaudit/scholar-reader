import { PDFDocumentProxy } from "pdfjs-dist";
import React from "react";
import { Citation, Paper, Symbol } from "./types/api";
import { PDFPageView, PDFViewer } from "./types/pdfjs-viewer";

export interface State {
  citations: Readonly<Citation[]>;
  symbols: Readonly<Symbol[]>;
  papers: Readonly<Papers>;
  pages: Readonly<Pages>;
  pdfDocument: PDFDocumentProxy | null;
  pdfViewer: PDFViewer | null;

  setCitations(citations: Citation[]): void;
  setSymbols(symbols: Symbol[]): void;
  setPapers(papers: Papers): void;
  setPages(pages: Pages): void;
}

export type Papers = { [s2Id: string]: Paper };
export type Pages = { [pageNumber: number]: PageModel };

interface PageModel {
  /**
   * Timestamp of 'pagerendered' event that created this page.
   */
  timeOfLastRender: number;
  /**
   * Reference to pdf.js page view object.
   */
  view: PDFPageView;
}

export interface PaperId {
  id: string;
  type: "s2" | "arxiv";
}

const defaultState: State = {
  setCitations: (citations: Citation[]) => {
    return;
  },
  setSymbols: (symbols: Symbol[]) => {
    return;
  },
  setPapers: (papers: Papers) => {
    return;
  },
  setPages: (pages: Pages) => {
    return;
  },
  citations: [],
  symbols: [],
  papers: {},
  pages: {},
  pdfDocument: null,
  pdfViewer: null
};

export const ScholarReaderContext = React.createContext<State>(defaultState);