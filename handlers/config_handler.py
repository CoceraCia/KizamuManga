AVAILABLE_WBSITES = ["weebcentral"]


class ConfigHandler:
    @staticmethod
    def manga_web_is_available(name: str) -> bool:
        return True if name in AVAILABLE_WBSITES else False

    @staticmethod
    def retrieve_available_websites(to_str=False):
        if not to_str:
            return AVAILABLE_WBSITES
        
        txt = ""
        for i, website in enumerate(AVAILABLE_WBSITES, start=0):
            txt += f"{i} - {website}"
        return txt
