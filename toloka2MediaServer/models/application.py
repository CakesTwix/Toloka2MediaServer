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
    enable_dot_spacing_in_file_name: bool = True


def app_to_config(app):
    config = configparser.ConfigParser()
    # Serialize the Application dataclass to the config under the "Toloka" section
    config["Toloka"] = {f.name: str(getattr(app, f.name)) for f in fields(app)}
    return config


def config_to_app(config):
    if "Toloka" not in config:
        return None

    section = config["Toloka"]
    # Deserialize the "Toloka" section back into an Application dataclass
    kwargs = {}
    for f in fields(Application):
        if f.name in section:
            if f.type == int:
                kwargs[f.name] = int(section[f.name])
            elif f.type == bool:
                kwargs[f.name] = config.getboolean("Toloka", f.name)
            else:
                kwargs[f.name] = section[f.name]
    return Application(**kwargs)
