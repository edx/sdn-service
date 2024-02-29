# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/edx/sanctions/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                                         |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| sanctions/\_\_init\_\_.py                                                                    |        1 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/\_\_init\_\_.py                                                               |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/api/\_\_init\_\_.py                                                           |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/api/models.py                                                                 |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/api/serializers.py                                                            |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/api/tests/\_\_init\_\_.py                                                     |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/api/urls.py                                                                   |        4 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/api/v1/\_\_init\_\_.py                                                        |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/api/v1/tests/\_\_init\_\_.py                                                  |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/api/v1/urls.py                                                                |        6 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/api/v1/views.py                                                               |       51 |        0 |        8 |        0 |    100% |           |
| sanctions/apps/api\_client/sdn\_client.py                                                    |       25 |        2 |        2 |        1 |     89% |     73-78 |
| sanctions/apps/api\_client/tests/\_\_init\_\_.py                                             |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/core/\_\_init\_\_.py                                                          |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/core/constants.py                                                             |        3 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/core/context\_processors.py                                                   |        3 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/core/migrations/0001\_initial.py                                              |        8 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/core/migrations/0002\_auto\_20231018\_1919.py                                 |        4 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/core/migrations/0003\_user\_full\_name.py                                     |        4 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/core/migrations/\_\_init\_\_.py                                               |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/core/models.py                                                                |       21 |        1 |        2 |        1 |     91% |22->21, 36 |
| sanctions/apps/core/tests/\_\_init\_\_.py                                                    |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/core/tests/factories.py                                                       |       15 |        0 |        4 |        0 |    100% |           |
| sanctions/apps/core/views.py                                                                 |       38 |        0 |        6 |        1 |     98% |    20->19 |
| sanctions/apps/sanctions/apps.py                                                             |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/sanctions/management/\_\_init\_\_.py                                          |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/sanctions/management/commands/\_\_init\_\_.py                                 |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/sanctions/management/commands/populate\_sdn\_fallback\_data\_and\_metadata.py |       57 |       10 |       14 |        4 |     80% |39-50, 58->exit, 75->58, 82->75, 84->89 |
| sanctions/apps/sanctions/management/commands/tests/\_\_init\_\_.py                           |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/sanctions/migrations/0001\_initial.py                                         |       10 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/sanctions/migrations/0002\_rename\_fallback\_models.py                        |        5 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/sanctions/migrations/0003\_auto\_20231109\_2121.py                            |        4 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/sanctions/migrations/\_\_init\_\_.py                                          |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/sanctions/models.py                                                           |       86 |        3 |       22 |        9 |     89% |92->91, 106->116, 107-112, 122->124, 123->122, 124->123, 157->156, 170->172, 217->216 |
| sanctions/apps/sanctions/tests/\_\_init\_\_.py                                               |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/apps/sanctions/tests/factories.py                                                  |       21 |        0 |        2 |        0 |    100% |           |
| sanctions/apps/sanctions/utils.py                                                            |       66 |       12 |       14 |        4 |     75% |33-43, 78, 104->109, 114-115, 180->187 |
| sanctions/apps/sanctions/views.py                                                            |        0 |        0 |        0 |        0 |    100% |           |
| sanctions/urls.py                                                                            |       10 |        0 |        0 |        0 |    100% |           |
|                                                                                    **TOTAL** |  **442** |   **28** |   **74** |   **20** | **90%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/edx/sanctions/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/edx/sanctions/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/edx/sanctions/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/edx/sanctions/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fedx%2Fsanctions%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/edx/sanctions/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.