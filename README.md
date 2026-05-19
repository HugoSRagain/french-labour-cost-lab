\# French Labour Cost Lab



\*\*French Labour Cost Lab\*\* is an open-source research project for simulating, documenting and visualizing labour costs in France.



The project focuses on:



\- gross monthly wages;

\- net monthly wages;

\- employer labour costs;

\- employer and employee social contributions;

\- social wedges;

\- cost-to-net ratios.



\## Status



Version 0.1.0 is a prototype. It uses stylized assumptions to validate the data pipeline, figures and dashboard.



Future versions will connect the simulation engine to official Mon-entreprise calculations.



\## Project structure



```text

french-labour-cost-lab/

├── scripts/

│   ├── build\_dataset.py

│   ├── make\_figures.py

│   └── build\_dashboard.py

├── data/

│   └── labour\_cost\_grid.csv

├── figures/

├── docs/

│   └── index.html

├── config/

│   └── scenarios.yml

├── requirements.txt

└── README.md

