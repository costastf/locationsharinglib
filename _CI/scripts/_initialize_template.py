import os
import sys
import logging


# This is the main prefix used for logging
LOGGER_BASENAME = '''_CI._initialize_template'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def add_ci_directory_to_path():
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    ci_path = os.path.abspath(os.path.join(current_file_path, '..'))
    if ci_path not in sys.path:
        sys.path.append(ci_path)


def initialize_template_environment():
    from configuration import (LOGGING_LEVEL,
                               ENVIRONMENT_VARIABLES,
                               PREREQUISITES)
    from library import (setup_logging,
                         validate_binary_prerequisites,
                         validate_environment_variable_prerequisites,
                         is_venv_created,
                         execute_command,
                         load_environment_variables,
                         load_dot_env_file,
                         activate_virtual_environment)
    load_environment_variables(ENVIRONMENT_VARIABLES)
    load_dot_env_file()
    if not validate_binary_prerequisites(PREREQUISITES.get('executables', [])):
        LOGGER.error('Prerequisite binary missing, cannot continue.')
        raise SystemExit(1)
    if not validate_environment_variable_prerequisites(PREREQUISITES.get('environment_variables', [])):
        LOGGER.error('Prerequisite environment variable missing, cannot continue.')
        raise SystemExit(1)

    if not is_venv_created():
        LOGGER.debug('Trying to create virtual environment.')
        success = execute_command('pipenv install --dev  --ignore-pipfile')
        if success:
            activate_virtual_environment()
            from emoji import emojize
            LOGGER.info('%s Successfully created virtual environment and loaded it! %s',
                        emojize(':white_heavy_check_mark:'),
                        emojize(':thumbs_up:'))
        else:
            LOGGER.error('Creation of virtual environment failed, cannot continue, '
                         'please clean up .venv directory and try again...')
            raise SystemExit(1)
    setup_logging(os.environ.get('LOGGING_LEVEL') or LOGGING_LEVEL)


def bootstrap_template():
    add_ci_directory_to_path()
    from library import activate_template
    activate_template()
    initialize_template_environment()


bootstrap_template()
