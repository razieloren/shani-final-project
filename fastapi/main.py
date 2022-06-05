#!/usr/bin/env python3

from imp import reload
import uvicorn

from api.api import app

if __name__ == '__main__':
    uvicorn.run(app, port=8080, host='0.0.0.0')