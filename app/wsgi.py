from importlib import import_module

Koinu = import_module('Koinu')
application = Koinu.app

if __name__ == "__main__":
  application.run()
