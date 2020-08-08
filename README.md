# SCT-USD

This repo allows the conversion of SCT (Spatial Camera Tracker) .dat files to [Pixar's Universal Scene Description](http://graphics.pixar.com/usd/docs/index.html).

If ffmpeg is installed to the path then it can also convert the exported video into a sequence of images

Currently this only supports camera data, but USDSkel conversion will be added in the future.

Technically this code also functions as a python reader for SCT .dat files too... 

## Running

To run this, you will need to have the USD python bindings in your `PYTHONPATH`.

## Attribution

SCT was created by [Kodholmen](https://github.com/Kodholmen) and is available on the iOS app store [here](https://apps.apple.com/app/id1521907061).
