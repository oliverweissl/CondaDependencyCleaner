<img align="right" width="175" height="175" src="./CDC.png"></img>
## CondaDependencyCleaner
![CI Status](https://github.com/oliverweissl/CondaDependencyCleaner/actions/workflows/main.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![conda-dependency-cleaner Downloads Last Month](https://assets.piptrends.com/get-last-month-downloads-badge/conda-dependency-cleaner.svg 'conda-dependency-cleaner Downloads Last Month by pip Trends')](https://piptrends.com/package/conda-dependency-cleaner)

A tool that helps make your conda environment files more lightweight by removing unnecessary transitive dependencies, leaving only what’s essential. 
It's a work-in-progress project, and we welcome feedback! 
Have ideas for new features or improvements? Open an issue in the repository to share your suggestions.

### How to use:
It is required to have conda installed. Once you are in a conda environment install conda `conda install conda` this is necessary for the package to work properly in the first place.
Then simply `pip install conda_dependency_cleaner`. 

Once installed you can clean your `.yaml` or `.yml` files by running the command `clean-yaml`. 
An example usage is as follows: 
```
clean-yaml env.yml -nf env_cleaned.yml
```

For help and more info use `clean-yaml --help`.
