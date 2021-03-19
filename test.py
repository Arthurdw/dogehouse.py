# -*- coding: utf-8 -*-
# MIT License

# Copyright (c) 2021 Arthur

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
from dogehouse import DogeClient

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

client = DogeClient("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJKb2tlbiIsImV4cCI6MTYxNjE4NTk2OSwiaWF0IjoxNjE2MTgyMzY5LCJpc3MiOiJKb2tlbiIsImp0aSI6IjJwbXRhamI3MGhuZWFoMzFyODAwNDQ0MSIsIm5iZiI6MTYxNjE4MjM2OSwidXNlcklkIjoiYTkzMTliYjgtOTIyMS00NWFiLWJkZWUtYzA3OTM4MGEyZmNlIn0.UEG4eYbjODlMvgNI0HfivSL61OOqu0c2LCC_DD6FWQk", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJKb2tlbiIsImV4cCI6MTYxODc3NDM2OSwiaWF0IjoxNjE2MTgyMzY5LCJpc3MiOiJKb2tlbiIsImp0aSI6IjJwbXRhamI3MHJoMWFoMzFyODAwNDQ1MSIsIm5iZiI6MTYxNjE4MjM2OSwidG9rZW5WZXJzaW9uIjoxLCJ1c2VySWQiOiJhOTMxOWJiOC05MjIxLTQ1YWItYmRlZS1jMDc5MzgwYTJmY2UifQ.KJNqLyfkOtLyfr8IFOK7f1Ufb1C7kAGIsWaNHTyhMZA")
client.run()
