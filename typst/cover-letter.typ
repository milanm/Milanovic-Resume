// Cover letter in the same style as the resume.
// Compile: typst compile --font-path ../fonts cover-letter.typ
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
)

#letter(
  recipient: [
    *Ms. Laura Kim* \
    VP of Engineering, Northwind Logistics \
    Amsterdam, Netherlands
  ],
  date: [23 November 2026],
  signature: [Dr. Milan Milanović],
)[
  Dear Ms. Kim,

  Northwind is moving its dispatch platform to the cloud while volume doubles every year. I have spent
  the last four years doing exactly that for a SaaS trucking platform, and I would like to do it for
  your team as Head of Platform Engineering.

  At 3MD I co-founded the platform and designed its architecture. It now handles 500 requests per second
  at 200 ms p95. When the Azure bill grew faster than revenue, I collapsed 14 microservices into a modular
  monolith and cut the bill by 30%. Deployments went from two days to 45 minutes once we automated CI/CD.

  Before that, at Zühlke, I grew a cloud practice from 6 to 28 engineers and kept 95% of them. Three
  became principals. I care about that number as much as the uptime numbers, because the team is what
  keeps the system running after I stop looking at it.

  Your job post mentions reliability targets and a team that is about to triple. I have hired, coached
  and promoted engineers through that kind of growth, and I would welcome a conversation about how I
  could help.

  Thank you for your time.

  Sincerely,
]
