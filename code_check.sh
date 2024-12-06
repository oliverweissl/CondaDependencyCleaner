#!/bin/bash
python -m black . --line-length 100 --preview

arr=("conda_dependency_cleaner" "tests")
for elem in "${arr[@]}"
do
  darglint -s sphinx "${elem}/."
  pyflakes "${elem}/."
  isort --profile black "${elem}/."
done