// Milanovic Resume (Typst): one page, one column, ATS-friendly.
// Compile: typst compile --font-path ../fonts resume.typ
#import "lib.typ": *

#show: resume.with(
  name: "Dr. Milan Milanović",
  contact: (
    [Belgrade, Serbia],
    link("mailto:milan@example.com")[milan\@example.com],
    [+381 60 123 456],
    link("https://www.linkedin.com/in/milanmilanovic")[linkedin.com/in/milanmilanovic],
  ),
  headline: "CTO / Principal Software Architect",
  tagline: "Builds cloud products and teams that scale to millions and cuts time-to-market by 50%",
  keywords: ("CTO", "Software Architect", ".NET", "Azure", "Engineering Leadership"),
  // paper: "us-letter", accent: rgb("#1F4E79"), font-size: 10.5pt,
)

#summary[
  Engineering leader with 20+ years of hands-on experience turning complex business ideas into
  reliable, scalable software. Grew a SaaS line to €1M ARR, cut Azure spend 30% (€120K/yr), and
  coached a 40-person team to deploy to production every 45 minutes at 99.9% uptime.
]

= Skills
#skills(
  [Technical strategy & roadmapping],
  [Microservices & modular monoliths],
  [Team scaling & people management],
  [.NET & C\# architecture],
  [Domain-Driven Design (DDD)],
  [Recruiting, mentoring & coaching],
  [Azure & cloud-native design],
  [DevOps & CI/CD (Azure DevOps, Git)],
  [Agile & Scrum leadership],
  [Security & compliance],
)

= Professional Experience

#job("3MD Inc", title: "Chief Technology Officer", location: "Belgrade, Serbia", dates: "2022 – Present")[
  - Co-founded and defined the architecture of a SaaS trucking platform processing 500 req/s at 200 ms p95 latency.
  - Hired and mentored a team of 10+ senior .NET engineers; set up the engineering ladder and OKR process.
  - Cut the Azure bill 30% by collapsing 14 microservices into a modular monolith (AKS to App Service).
  - Introduced automated CI/CD; deployments shrank from 2 days to 45 minutes.
  - Introduced real-time cost dashboards and rightsizing routines; trimmed compute spend by €120K/yr and met ISO 27001 controls ahead of the audit.
]

#job("Zühlke Group", title: "Principal Consultant", location: "Belgrade, Serbia", dates: "2017 – 2022")[
  - Closed a US\$2M consulting engagement by designing an integrated investment advisory solution; delivered 107% YoY client growth.
  - Architected a speech recognition platform on Azure Cognitive Services with transcript latency under 300 ms at a 99.9% SLO.
  - Led the cloud capability for the SEE region; ran 12 masterclasses and certified 25 architects on Azure.
  - Scaled the cloud practice from 6 to 28 engineers; 95% retention, three future principals promoted.
  - Promoted twice in 3 years for impact on revenue and engineering excellence.
]

#job("EPS", title: "Head of Engineering", location: "Belgrade, Serbia", dates: "2004 – 2017")[
  - Managed a 40-person department delivering internal line-of-business apps used by 10K employees.
  - Standardized the SDLC and CI, raising on-time delivery from 60% to 92% within 12 months.
  - Cut Severity 1 production outages by 40% in 12 months.
]

= Education
- #education("Ph.D. in Computer Science", school: "University of Belgrade", year: "2010")
- #education("M.Sc. in Software Engineering", school: "University of Belgrade", year: "2007")
- #education("B.Sc. (Hons.) in Computer Engineering Management", school: "School of Business", year: "2004 (GPA 4.0/4.0)")

= Certifications
#inline[Microsoft MVP][Azure Developer][Certified ScrumMaster (CSM)][Professional Scrum Developer (PSD)]

= Languages
#inline[Serbian (native)][English (C1)]
