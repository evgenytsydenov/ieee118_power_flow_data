# Contribution Guide

Everyone is welcome to contribute to this project. Feel free to share your ideas to improve the dataset and make it more valuable to the power engineering community.

## How to contribute

If you have found a bug or have a suggestion, please open [an issue](https://github.com/evgenytsydenov/ieee118_power_flow_data/issues) to discuss possible new developments with the community and developers.

If you can fix a problem or implement a new feature yourself, please read the following steps to learn how to submit your suggestions via pull requests:
1. Create a fork using the "Fork" button in the repository. This creates a copy of the code under your GitHub user account and allows you to freely experiment with changes without affecting the original project (see [GitHub docs](https://docs.github.com/en/get-started/quickstart/contributing-to-projects#forking-a-repository) for details).
2. Clone your fork to your local disk, and add the base repository as a remote:
    ```shell
    $ git clone https://github.com/<YOUR_GITHUB_USERNAME>/ieee118_power_flow_data.git
    $ cd ieee118_power_flow_data
    $ git remote add upstream https://github.com/evgenytsydenov/ieee118_power_flow_data.git
    ```
3. Create a new branch to hold your development changes:
    ```shell
    $ git checkout -b <BRANCH_NAME>
    ```
4. Set up a development environment using [poetry](https://python-poetry.org/docs/) by running the following command:
    ```shell
    $ poetry install --with dev
    ```
   or, if you prefer [pip](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/), create and activate virtual environment, and run the following command:
    ```shell
    $ pip install -r requirements-dev.txt
    ```
5. Develop on your branch. Please follow [the project considerations](#Project-considerations) listed below.
6. Once you finished developing, install pre-commit hooks:
    ```shell
    $ pre-commit install
    ```
    add changed files and make a commit to record your changes locally:
    ```shell
    $ git add .
    $ git commit -m "Add: commit message"
    ```
   sync your code with the original repository:
    ```shell
    $ git fetch upstream
    $ git rebase upstream/main
    ```
   push the changes to your account:
    ```shell
    $ git push -u origin <BRANCH_NAME>
    ```
7. Go to the webpage of your fork on GitHub, choose your branch, click on "Pull request" to send your changes for review (see [GitHub docs](https://docs.github.com/en/get-started/quickstart/contributing-to-projects#making-a-pull-request) for details). The title of your pull request should be a summary of its contribution.
8. Your changes are now visible for everyone [on the Pull requests page](https://github.com/evgenytsydenov/ieee118_power_flow_data/pulls). We will review your pull request as soon as possible!

## Project considerations

1. Commit messages should have the following format: "\<tag>: \<message>", where \<tag> is one of "Add", "Update" or "Fix".
2. Branch names should be informative and [snake_case](https://en.wikipedia.org/wiki/Snake_case) formatted.
3. All methods and classes should be documented. We try to adhere by [the Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings).
4. We use [PEP8](https://peps.python.org/pep-0008/) (with max line length equal to 88) and check that the code is formatted with [black](https://black.readthedocs.io/en/stable/index.html).


## Possible enhancements

Here is a list of topics that can be implemented to enhance the quality of the dataset (in descending order of priority):

1. Bus voltage limits can be set from the JEAS-118 dataset. Currently, these values are hardcoded as 0.8 and 1.2 for `min_v_pu` and `max_v_pu` respectively to achieve the convergence of the OPF estimation.
2. Min limits of active output of optimized generators are currently set to zero to achieve the convergence of the OPF estimation. These limits can be set according to the NREL-118 data.
3. Limits of reactive output of generators can be estimated more accurate with consideration of actual active output of generators. Currently, the limits are set from -0.3 to 0.7 of the max active output.
4. The cost function used for the OPF task can be composed and added to reflect the unit commitment process used in the industry. Currently, the default cost function from PandaPower is used which aims to minimize the total generation.
5. Branch outages can be added as time series to simulate emergency failures or maintenance during the year. At present, all branches are always in service.
6. The NREL-118 dataset contains a lot of generator parameters (fuel price, emission rate, start cost, up and down time, speed and cost of ramp up and down, etc.) that can be used to solve the OPF task in a more realistic way.
7. The JEAS-118 dataset contains information about angles of phase shifting transformers. These angles can be added to the power system model for more accurate transformer modeling.
8. Limits of slack bus injections can be added as time series for more realistic simulation of external grid behavior.
9. The `PLANT_MODE` parameter can be added to group generators per buses so that the power system model contains only one generator/plant per bus.
10. Memory consumption of parallel execution of OPF and PF (in workers) can be optimized by using [the shared memory](https://docs.python.org/3/library/multiprocessing.shared_memory.html).
