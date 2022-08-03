# Getting started with Enviro


## An overview of what's on the board

TODO: diagram of board features

On the front:

- ① **POKE** button: wakes the board from sleep to take an ad hoc reading
- ② **ACTIVITY** white LED: pulses gently when the board is awake (quickly when in provisioning mode)
- ③ **WARNING** red LED: blinks if an error occurs (e.g. the wireless connection is down)
- ④ Qw/ST connector: a convenient way to add extra sensors
- ⑤ Sensors: the collection of sensors that the board gathers data from (vary depending on board type)

On the rear:

- ⑥ **RESET** button (rea): resets the board (hold **POKE** while resetting to force back into provisioning mode)
- ⑦ Battery connector: JST type connector compatible with many battery holders and cells
- ⑧ USB connector: microB USB connector for accessing logs and reading files

## Setting up

When you recieve your Enviro board it will come preloaded with our software but will not be configured yet. You need to go through the provisioning process to tell it how to connect to your wireless network, when to take readings, and optionally where to upload them.

Follow these instructions to get your Enviro board configured and running:

### Step 1: Power up

Plug in your battery or USB cable and press the **POKE** button on the front of the board. The **ACTIVITY** LED will pulse slowly.

If you haven't previously configured this board then it will detect that it has not yet been configured and automatically go into provisioning (setup) mode. The **ACTIVITY** LED will  pulse rapidly.

*Note: You can use 3xAA or 3xAAA (either alkaline or HiMH) or a single cell LiPo battery to power Enviro.*

### Step 1: Connect to your Enviro

Once in provisioning mode your Enviro will appear as a new wireless network that you can connect to.

<img src="images/access-point-network.png">

*Enviro showing up as an access point during provisioning mode*

Use your phone, tablet, or computer to connect to this network and after a few seconds the setup process will start.

