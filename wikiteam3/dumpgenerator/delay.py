import itertools
import threading
import time
import sys


class Delay:

    done: bool = True
    ellipses: str = "."

    def animate(self):
        try:
            while not self.done:
                print("\r" + self.ellipses, end="")
                self.ellipses += "."
                time.sleep(0.1)
        except KeyboardInterrupt:
            sys.exit()

    def __init__(self, config={}, session=None):
        """Add a delay if configured for that"""
        if config["delay"] > 0:
            self.done = False

            ellipses_animation = threading.Thread(target=self.animate)
            ellipses_animation.start()

            # sys.stdout.write("\rSleeping %.2f seconds..." % (config["delay"]))
            # sys.stdout.flush()

            time.sleep(config["delay"])
            self.done = True

            spaces = int(config["delay"]/0.1)
            print("\r"+" "*spaces,end="\r")
