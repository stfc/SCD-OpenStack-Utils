import sys
import os

sys.path.insert(0, '/var/www/app')

from app import create_app

application = create_app()

if __name__ == '__main__':
    application.run()
