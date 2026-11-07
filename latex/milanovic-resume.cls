%% milanovic-resume.cls
%% A one-page, single-column, ATS-friendly resume class.
%% Author: Dr. Milan Milanovic (https://github.com/milanm/Milanovic-Resume)
%% License: MIT (class and examples), SIL OFL 1.1 (bundled Source Sans 3 fonts)
%%
%% Compile with LuaLaTeX (latexmkrc in this folder sets it up; Overleaf: Menu > Compiler > LuaLaTeX).
%% LuaLaTeX writes real hyphens and spaces into the PDF text layer and, with the
%% \DocumentMetadata line at the top of each example, a tagged PDF/UA-2 file.
%% XeLaTeX also works: delete the \DocumentMetadata line first (XeTeX can't tag).
%%
%% Class options (all optional, key=value):
%%   paper     = a4 | letter            (default: a4)
%%   accent    = <hex colour, no #>     (default: 003366, navy)
%%   fontsize  = <points>               (default: 11; "10.5" and "10.5pt" both work)
%%   ligatures = true | false           (default: false, keeps "fi"/"fl" extractable for ATS parsers)
%%   onepage   = true | false           (default: true, warns if the resume spills onto page 2)

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{milanovic-resume}[2026/11/07 v1.0 Milanovic Resume]

% ---------------------------------------------------------------- options
\RequirePackage{kvoptions}
\SetupKeyvalOptions{family=MR,prefix=MR@}
\DeclareStringOption[a4]{paper}
\DeclareStringOption[003366]{accent}
\DeclareStringOption[11]{fontsize}
\DeclareBoolOption[false]{ligatures}
\DeclareBoolOption[true]{onepage}
\ProcessKeyvalOptions*

\LoadClass{article}

% ---------------------------------------------------------------- page
\def\MR@letter{letter}
\ifx\MR@paper\MR@letter
  \RequirePackage[letterpaper,top=1.4cm,bottom=1.3cm,left=1.6cm,right=1.5cm]{geometry}
\else
  \RequirePackage[a4paper,top=1.4cm,bottom=1.3cm,left=1.75cm,right=1.5cm]{geometry}
\fi
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0pt}
\raggedbottom
% Left-aligned text, no hyphenation: easier to scan, and parsers never see split words.
\AtBeginDocument{\raggedright}
\hyphenpenalty=10000
\exhyphenpenalty=10000
\frenchspacing

% ---------------------------------------------------------------- colour
\RequirePackage{xcolor}
\definecolor{accent}{HTML}{\MR@accent}
\definecolor{rule}{HTML}{000000}

% ---------------------------------------------------------------- fonts
% Source Sans 3 is bundled in ../fonts (or ./fonts on Overleaf).
% If neither folder exists, fontspec looks for an installed copy.
\RequirePackage{fontspec}
% XeTeX maps some glyphs back to the wrong character in the PDF text layer
% (a plain hyphen comes out as U+2011, so "cloud-native" no longer matches a
% keyword search). ActualText spans keep the characters you typed.
\ifdefined\XeTeXgenerateactualtext\XeTeXgenerateactualtext=1\fi
\def\MR@fontpath{}
\IfFileExists{fonts/SourceSans3-Regular.otf}{\def\MR@fontpath{fonts/}}{}
\IfFileExists{../fonts/SourceSans3-Regular.otf}{\def\MR@fontpath{../fonts/}}{}
\ifMR@ligatures
  \def\MR@ligs{TeX}
\else
  \def\MR@ligs{{TeX,NoCommon}}
\fi
\setmainfont{SourceSans3}[
  Path           = \MR@fontpath,
  Extension      = .otf,
  UprightFont    = *-Regular,
  ItalicFont     = *-It,
  BoldFont       = *-Bold,
  BoldItalicFont = *-BoldIt,
  FontFace       = {sb}{n}{*-Semibold},
  FontFace       = {sb}{it}{*-SemiboldIt},
  Ligatures      = \MR@ligs
]
\newcommand\semibold{\fontseries{sb}\selectfont}

% Base size: scale everything from the fontsize option (accepts 10.5 or 10.5pt).
\def\MR@stripPt#1pt#2\@nil{\def\MR@fontsize{#1}}
\expandafter\MR@stripPt\MR@fontsize pt\@nil
\newlength\MR@fs \setlength\MR@fs{\MR@fontsize pt}
\newlength\MR@bs \setlength\MR@bs{1.25\MR@fs}
\renewcommand\normalsize{\fontsize{\MR@fs}{\MR@bs}\selectfont}
\renewcommand\small{\fontsize{0.93\MR@fs}{1.15\MR@fs}\selectfont}
\renewcommand\footnotesize{\fontsize{0.86\MR@fs}{1.08\MR@fs}\selectfont}
\renewcommand\large{\fontsize{1.12\MR@fs}{1.36\MR@fs}\selectfont}
\renewcommand\Huge{\fontsize{2.25\MR@fs}{2.6\MR@fs}\selectfont}
\normalsize

% ---------------------------------------------------------------- packages
\RequirePackage{enumitem}
\RequirePackage{multicol}
\RequirePackage[hidelinks,unicode,pdfusetitle]{hyperref}
\RequirePackage{bookmark}

% Bullets: real characters, so the PDF text layer keeps them.
\setlist[itemize]{
  label={\textbullet},
  leftmargin=1.55em,
  labelsep=0.55em,
  itemsep=1.2pt,
  parsep=0pt,
  topsep=2pt,
  partopsep=0pt
}
\setlist[itemize,2]{label={\normalfont\textopenbullet}, topsep=0pt, leftmargin=1.3em}

% ---------------------------------------------------------------- header data
\def\MR@name{}
\def\MR@contact{}
\def\MR@headline{}
\def\MR@tagline{}
\def\MR@keywords{}
\newcommand\name[1]{\def\MR@name{#1}}
\newcommand\contact[1]{\def\MR@contact{#1}}
\newcommand\headline[1]{\def\MR@headline{#1}}
\newcommand\tagline[1]{\def\MR@tagline{#1}}
\newcommand\keywords[1]{\def\MR@keywords{#1}}

% Separator for inline lists: Belgrade · email · phone
\newcommand\sep{\unskip\hspace{0.45em}\textperiodcentered\hspace{0.45em}\ignorespaces}

\newcommand\MR@rule[1]{\par\nointerlineskip\noindent{\color{rule}\rule{\linewidth}{#1}}\par\nointerlineskip}

\newcommand\makeheader{%
  \hypersetup{
    pdftitle    = {\MR@name\space - Resume},
    pdfauthor   = {\MR@name},
    pdfsubject  = {Resume},
    pdfkeywords = {\MR@keywords},
    pdfcreator  = {milanovic-resume.cls}
  }%
  \pdfbookmark[1]{\MR@name}{header}%
  \begingroup\centering
    {\Huge\bfseries\color{accent}\MR@name\par}%
    \vspace{3pt}%
    {\small\MR@contact\par}%
  \endgroup
  \ifx\MR@headline\@empty\vspace{2pt}\else
    \vspace{5pt}\MR@rule{0.6pt}\vspace{3pt}%
    \begingroup\centering
      {\large\bfseries\color{accent}\MR@headline\par}%
      \ifx\MR@tagline\@empty\else
        \vspace{0.5pt}{\color{accent}\MR@tagline\par}%
      \fi
    \endgroup
    \vspace{3pt}\MR@rule{1.2pt}\vspace{4pt}%
  \fi
}

% ---------------------------------------------------------------- summary
\newcommand\summary[1]{%
  \par\addvspace{2pt}%
  {\setlength{\baselineskip}{1.32\MR@fs}#1\par}%
}

% ---------------------------------------------------------------- sections
% Centred, upper-case, accent colour, thin rule above and a thicker one below.
\newlength\MR@secskip \setlength\MR@secskip{9pt}
\renewcommand\section[1]{%
  \par\vspace{\MR@secskip}%
  \pdfbookmark[1]{#1}{sec:\thepage:\the\inputlineno}%
  \MR@rule{0.4pt}\vspace{2.5pt}%
  {\centering\large\bfseries\color{accent}\MakeUppercase{#1}\par}%
  \vspace{1.5pt}\MR@rule{0.8pt}%
  \nopagebreak\vspace{5pt}%
}

% ---------------------------------------------------------------- entries
% \job{Company}{Title}{Location}{Dates}
\newcommand\job[4]{%
  \par\addvspace{6pt}%
  \noindent{\bfseries #1\ifx\relax#2\relax\else\ -- #2\fi}%
  \ifx\relax#3\relax\else, #3\fi
  \hfill{\itshape #4}\par\nopagebreak
}

% \education{Degree}{School}{Year}
\newcommand\education[3]{%
  \item{\bfseries #1}\ifx\relax#2\relax\else\ -- #2\fi\ifx\relax#3\relax\else, #3\fi
}

% \project{Name}{Context}{Tech stack} followed by an itemize of results
\newcommand\project[3]{%
  \par\addvspace{3pt}%
  \noindent{\bfseries #1}\ifx\relax#2\relax\else\ (#2)\fi
  \ifx\relax#3\relax\else\hfill{\itshape\small #3}\fi\par\nopagebreak
}

% Skills. Default: one line of items separated by middle dots, so every parser
% reads them right after the SKILLS heading. \begin{skills}[columns] gives the
% two-column bullet list instead; it looks closer to a classic resume, but
% pdfminer.six reads its left column before the heading.
\newif\ifMR@firstskill
\def\MR@columnsword{columns}
\newenvironment{skills}[1][inline]{%
  \def\MR@skillstyle{#1}%
  \ifx\MR@skillstyle\MR@columnsword
    \setlength{\columnsep}{1.6em}%
    \setlength{\multicolsep}{0pt}%
    \begin{multicols}{2}\begin{itemize}[topsep=0pt]%
  \else
    % Each skill sits in an unbreakable box; lines break only after a dot.
    \par\noindent\MR@firstskilltrue
    \def\item{%
      \ifMR@firstskill\global\MR@firstskillfalse
      \else\unskip\egroup\nobreak\hspace{0.45em}\textperiodcentered\hspace{0.45em}\fi
      \hbox\bgroup\ignorespaces}%
    \setlength{\baselineskip}{1.32\MR@fs}%
  \fi
}{%
  \ifx\MR@skillstyle\MR@columnsword
    \end{itemize}\end{multicols}\vspace{3pt}%
  \else
    \unskip\egroup\par\vspace{2pt}%
  \fi
}

% Plain line for certifications, languages, awards.
\newcommand\inline[1]{\par\noindent #1\par\vspace{2pt}}

% ---------------------------------------------------------------- cover letter
\def\MR@recipient{}
\def\MR@letterdate{\today}
\newcommand\recipient[1]{\def\MR@recipient{#1}}
\newcommand\letterdate[1]{\def\MR@letterdate{#1}}
\newenvironment{letter}{%
  \par\addvspace{10pt}%
  \noindent\begin{minipage}[t]{0.6\linewidth}\MR@recipient\end{minipage}%
  \hfill\begin{minipage}[t]{0.35\linewidth}\raggedleft\MR@letterdate\end{minipage}\par
  \vspace{14pt}%
  \setlength{\parskip}{0.75\baselineskip}%
  \setlength{\baselineskip}{1.32\MR@fs}%
}{\par}
\newcommand\signature[1]{\par\vspace{1.2\baselineskip}{\bfseries\color{accent}#1}\par}

% ---------------------------------------------------------------- one-page guard
% Prints a warning in the log when the resume runs past page 1. "One page. Period." Turn it off with onepage=false.
\ifMR@onepage
  \AtEndDocument{%
    \ifnum\value{page}>1
      \ClassWarningNoLine{milanovic-resume}{Your resume runs to \thepage\space pages. Cut until it fits on one}%
    \fi
  }
\fi

\endinput
