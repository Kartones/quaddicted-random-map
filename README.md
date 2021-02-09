# Quaddicted Random Map

## Intro

I love [Quake](https://en.wikipedia.org/wiki/Quake_(video_game)). [Quake is forever](https://www.quaddicted.com/_media/quake/quake_is_forever.jpg).

I also like a lot the [Quaddicted site](https://www.quaddicted.com/), but their [Quake Injector](https://www.quaddicted.com/tools/quake_injector) launcher a) didn't worked on my Linux laptop and b) I just wanted a way to enjoy new quake maps with ease.

As the familiar expression says, `"A Quake map a day keeps boredom away"`.

## Setup

Only providing instructions for linux, but pull requests are welcomed.

### Linux

Install python 3 if needed:
```
sudo apt-get update
sudo apt-get install python3
```

Install pip3 if needed:
```
sudo apt-get update
sudo apt install python3-pip
```

Install this project requirements:
```
pip3 install -r requirements.txt
```

### Windows

Install python 3 if needed: https://www.python.org/downloads/windows/

Install this project requirements:
```
pip3 install -r requirements.txt
```


## Running

Only providing instructions for linux, but pull requests are welcomed.

Execute from a command line at your Quake root folder.

```
python3 quaddicted-random-map.py
```

To select another engine (default is [vkQuake](https://github.com/Novum/vkQuake)), use `--engine` param:
```
python3 quaddicted-random-map.py --engine ./quakespasm
```

If you don't have the python file in the same folder as quake, use `--path <...>` param:
```
python3 /<somepath>/quaddicted-random-map.py --path ./
```


## License

See [LICENSE](LICENSE).
