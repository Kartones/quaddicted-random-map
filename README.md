# Quaddicted Random Map

## Intro

```plain
     .::-           .::.
   .::                 ::.
  :6.                    ::
 :6                       6:
-6:                       :6-
:6.                        66
66-                       .66
66:                       :66
:66:       -:::::-       :66:
 :66:       .666-       :66:
  :666:.     666     .:666:
   .:6666:...666.-::66666:
     .:6666666666666666:
        .-:6666666::-
             666
             666
             666
             :6:
              6.
              :
```

I love [Quake](https://en.wikipedia.org/wiki/Quake_(video_game)). [Quake is forever](https://www.quaddicted.com/_media/quake/quake_is_forever.jpg).

I also like a lot the [Quaddicted site](https://www.quaddicted.com/), but their [Quake Injector](https://www.quaddicted.com/tools/quake_injector) launcher a) didn't worked on my Linux laptop and b) I just wanted a way to enjoy new quake maps with ease.

As the familiar expression says, `"A Quake map a day keeps boredom away"`.

## Setup

### Linux

Install python 3 if needed:

```bash
sudo apt-get update
sudo apt-get install python3
```

Install pip3 if needed:

```bash
sudo apt-get update
sudo apt install python3-pip
```

Install this project requirements:

```bash
pip3 install -r requirements.txt
```

### MacOS

Install python3 using [Brew](https://brew.sh/) (recommended)

```bash
brew install python3
```

Install this project requirements:

```bash
pip3 install -r requirements.txt
```

### Windows

Install python 3 if needed: <https://www.python.org/downloads/windows/>

Install this project requirements:

```powershell
pip3 install -r requirements.txt
```

## Running

Execute from a command line at your Quake root folder.

### Linux

```bash
python3 quaddicted-random-map.py
```

To select another engine (default is [vkQuake](https://github.com/Novum/vkQuake)), use `--engine` param:

```bash
python3 quaddicted-random-map.py --engine ./quakespasm
```

If you don't have the python file in the same folder as quake, use `--path <...>` param:

```bash
python3 /<somepath>/quaddicted-random-map.py --path /<someotherpath>/Quake
```

### Windows

```bash
python quaddicted-random-map.py
```

To select another engine (default is [vkQuake](https://github.com/Novum/vkQuake)), use `--engine` param (no need to add `.exe` extension):

```powershell
python quaddicted-random-map.py --engine quakespasm
```

etcetera (see Linux version for other parameters)

## License

See [LICENSE](LICENSE).
