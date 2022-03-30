# from random_user_agent.user_agent import UserAgent as _UserAgent
# from random_user_agent.params import HardwareType, SoftwareType


class UserAgent:
    """Return a cool user-agent to hide Python user-agent"""

    # user_agent_rotator: _UserAgent = _UserAgent(
    #     hardware_types=[HardwareType.COMPUTER],
    #     software_types=[SoftwareType.WEB_BROWSER],
    #     limit=100,
    # )

    def __init__(self):
        pass

    def __str__(self) -> str:
        useragents = [
            # firefox
            # 'Mozilla/5.0 (X11; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
            # 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
            "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0"
        ]
        return useragents[0]
        # return self.user_agent_rotator.get_random_user_agent()
