import datetime

from .version import getVersion


def print_welcome():
    print("")
    """Opening message"""
    print("#" * 73)
    print(
        "# Welcome to DumpGenerator %s by WikiTeam (GPL v3)                   #"
        % getVersion()
    )
    print(
        "# More info at: https://github.com/WikiTeam/wikiteam                    #" ""
    )
    print("#" * 73)
    print("")
    print("#" * 73)
    print(
        "# Copyright (C) 2011-%d WikiTeam developers                           #"
        % (datetime.datetime.now().year)
    )
    print("#" + " " * 71 + "#")
    print("# This program is free software: you can redistribute it and/or modify  #")
    print("# it under the terms of the GNU General Public License as published by  #")
    print("# the Free Software Foundation, either version 3 of the License, or     #")
    print("# (at your option) any later version.                                   #")
    print("#                                                                       #")
    print("# This program is distributed in the hope that it will be useful,       #")
    print("# but WITHOUT ANY WARRANTY; without even the implied warranty of        #")
    print("# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #")
    print("# GNU General Public License for more details.                          #")
    print("#                                                                       #")
    print("# You should have received a copy of the GNU General Public License     #")
    print("# along with this program.  If not, see <http://www.gnu.org/licenses/>. #")
    print("#" * 73)
    print("")

    return


def bye():
    """Closing message"""
    print("")
    print("---> Congratulations! Your dump is complete <---")
    print("")
    print("If you found any bug, report a new issue here:")
    print("  https://github.com/WikiTeam/wikiteam/issues")
    print("")
    print("If this is a public wiki, please, consider publishing this dump.")
    print("Do it yourself as explained in:")
    print("  https://github.com/WikiTeam/wikiteam/wiki/Tutorial#Publishing_the_dump")
    print("Or contact us at:")
    print("  https://github.com/WikiTeam/wikiteam")
    print("")
    print("Good luck! Bye!")
    print("")
