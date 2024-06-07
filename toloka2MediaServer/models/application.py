from dataclasses import dataclass, fields
import configparser

@dataclass
class Application:
    username: str = ""
    password: str = ""
    client: str = ""
    default_download_dir: str = ""
    default_meta: str = ""
    wait_time: int = 0
    client_wait_time: int = 0

def app_to_config(app):
    config = configparser.ConfigParser()
    # Serialize the Application dataclass to the config under the "Toloka" section
    config['Toloka'] = {f.name: getattr(app, f.name) if not isinstance(getattr(app, f.name), int) else str(getattr(app, f.name))
                        for f in fields(app)}
    return config

def config_to_app(config):
    if 'Toloka' not in config:
        return None

    section = config['Toloka']
    # Deserialize the "Toloka" section back into an Application dataclass
    kwargs = {
        f.name: (int(section[f.name]) if f.type == int else section[f.name])
        for f in fields(Application) if f.name in section
    }
    return Application(**kwargs)