packages <- c(
  "jsonlite", "readxl", "tidyverse", "cld3", "base64enc", "knitr",
  "tidytext", "topicmodels", "tm", "koRpus", "ldatuning",
  "openxlsx", "koRpus.lang.en", "koRpus.lang.nl"
)

# Install missing packages
new_packages <- packages[!(packages %in% installed.packages()[,"Package"])]
if(length(new_packages)) install.packages(new_packages, repos='http://cran.us.r-project.org')

# Load packages
lapply(packages, require, character.only = TRUE)