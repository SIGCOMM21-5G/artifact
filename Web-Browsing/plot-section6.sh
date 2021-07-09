#!/bin/bash

mkdir plots
python scripts/objectnum-plt-energy-analysis.py # generates objectnum-plt-energy-relation.pdf i.e. Figure 19a
python scripts/pagesize-plt-energy-analysis.py # generates objectnum-plt-energy-relation.pdf i.e. Figure 19b
python scripts/plot-cdf.py # generates cdf-energy.pdf and cdf-plt.pdf i.e. Figure 20
python scripts/energy-time-analysis.py # generates energy-plt-relation.pdf i.e. Figure 21
python scripts/tree-generation-M1.py # generates tree-M1.png i.e. Figure 22a.
python scripts/tree-generation-M4.py # generates tree-M4.png i.e. Figure 22b.
python scripts/interface-selection.py # generates Table 6.
echo "Success."
