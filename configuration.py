# load the configuration file
import yaml



def load_configuration(yaml_file='/home/axnow/ttconfig.yaml'):
    print(f'Loading configuration from file {yaml_file}')
    with open(yaml_file, 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            print(f'Read configuration from {yaml_file}, got {len(config)} root values.')
            return config
        except yaml.YAMLError as exc:
            print(f'Failed to load configuration from {yaml_file}')
            print(exc)
