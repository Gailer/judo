# JUDO

### Version: 1.0.0.0

## Requirements
Judo Device
This plugin is designed to retrieve data from a [JUDO](http://www.judo.eu/) device.

## Supported Hardware

Is currently working with the following modules:

  * JUDO isoft safe Plus
  
## Hint

water_daily => Verbrauch in 3 Stunden zusammengefasst, -1 = kein Verbrauch
  3 4 2 4 2 5
  => 0-3 Uhr = 3 Liter
  => 3-6 Uhr = 4 Liter
  => 6-9 Uhr = 2 Liter
  ...

 water_weekly => Verbrauch der Woche, Ergebnisse pro Tag beginnend mit Montag, -1 kein Verbrauch
  10 20 30 40 50 60 70
  => 10 Liter Montag
  => 20 Liter Dienstag 
  ...

 water_monthly => Verbrauch des Monats, pro Tag
  10 10 12 14 15
  => 10 Liter am 01.
  => 10 Liter am 02.
  => 12 Liter am 03.
  ...

 water_yearly => Verbrauch des Jahres, pro Monats
  100 200 205
  => 100 Liter im Januar
  => 200 Liter im Februar
  => 205 Liter im März 
  ...

 water_total => Verbrauch gesamt
  

## Configuration


### plugin.yaml

The plugin can be configured like this:

```yaml
Judo:
    class_name: Judo
    class_path: plugins.judo
    ipaddress: <IP-ADDRESS>
    port: 8124
    username: <USERNAME>
    password: <PASSWORD
    device_number: <DEVICE-NUMBER>
    cycle: 300    
```

This plugin retrieves data from a Judo module.

The data retrieval is done by establishing a network connection to the
inverter module and retrieving the status via a HTTP request.

You need to configure the IP address of the device.
It is used the user and password attributes to get a token. After the token we connect with token and the devicenumber.

The cycle parameter defines the update interval and defaults to 300 seconds.
The port defaults to 8124

### items.yaml

#### Description of all possible items

#### judo_cfg
This attribute defines supported functions that can be set for an item. See example below.

#### Example

```yaml
Judo:
    Enthaertungsanlage:
        name: Wasser (Judo)
        sv_page: room
        sv_hide: 'No'
        sv_img: measure_water_meter.svg
        sv_heading_center: ""
        
        hardness:
            residual:
                type: num
                judo_cfg: '{"group": "settings", "command": "residual hardness", "msgnumber": "1"}'
                database: Init
                                
        salt_consumtion:
            salt_quantity:
                type: num
                judo_cfg: '{"group": "consumption", "command": "salt quantity", "msgnumber": "1"}'
                eval: float(value)/1000
                database: Init
                
            salt_range:
                type: num
                judo_cfg: '{"group": "consumption", "command": "salt range", "msgnumber": "1"}'
                database: Init
                
        water_consumtion:
            daily:
                name: Wasserverbrauch täglich
                sv_blocksize: 1
                sv_widget: "{{ plot.period('', 'Judo.Enthaertungsanlage.water_consumtion.daily.water_daily', 'avg', '30d', 'now', '', '', 30, '', '', '', '', 'advanced') }}"
                struct: judo_water_struct
                water:
                    judo_cfg: '{"group": "consumption", "command": "water daily", "msgnumber": "1"}'
                    eval: value.strip().split(' ')
                    on_change:
                    - sh..water_1(sh..self()[0])
                    - sh..water_2(sh..self()[1])
                    - sh..water_3(sh..self()[2])
                    - sh..water_4(sh..self()[3])
                    - sh..water_5(sh..self()[4])
                    - sh..water_6(sh..self()[5])
                    - sh..water_7(sh..self()[6])
                    - sh..water_8(sh..self()[7])
                water_daily:                    
                    type: num
                    visu_acl: r
                    database: Init
                    crontab: 
                    - "55 23 * * = 1"                    
                    eval: max(0, sh...water.water_1()) + max(0, sh...water.water_2()) + max(0, sh...water.water_3()) + max(0, sh...water.water_4()) + max(0, sh...water.water_5()) + max(0, sh...water.water_6()) + max(0, sh...water.water_7()) + max(0, sh...water.water_8())
            weekly:
                name: Wasserverbrauch wöchentlich
                sv_blocksize: 1
                sv_widget: "{{ plot.period('', 'Judo.Enthaertungsanlage.water_consumtion.daily.water_weekly', 'avg', '52w', 'now', '', '', 52, '', '', '', '', 'advanced') }}"
                struct: judo_water_struct
                water:
                    judo_cfg: '{"group": "consumption", "command": "water weekly", "msgnumber": "1"}'
                    eval: value.strip().split(' ')
                    on_change:
                    - sh..water_1(sh..self()[0])
                    - sh..water_2(sh..self()[1])
                    - sh..water_3(sh..self()[2])
                    - sh..water_4(sh..self()[3])
                    - sh..water_5(sh..self()[4])
                    - sh..water_6(sh..self()[5])
                    - sh..water_7(sh..self()[6])
                water_weekly:
                    type: num
                    visu_acl: r
                    database: Init
                    crontab: 
                    - "55 23 * 7 = 1"                    
                    eval: max(0, sh...water.water_1()) + max(0, sh...water.water_2()) + max(0, sh...water.water_3()) + max(0, sh...water.water_4()) + max(0, sh...water.water_5()) + max(0, sh...water.water_6()) + max(0, sh...water.water_7())
                    
            monthly:
                name: Wasserverbrauch monatlich
                sv_blocksize: 1
                sv_widget: "{{ plot.period('', 'Judo.Enthaertungsanlage.water_consumtion.daily.water_monthly', 'avg', '12m', 'now', '', '', 12, '', '', '', '', 'advanced') }}"
                struct: judo_water_struct
                water:
                    judo_cfg: '{"group": "consumption", "command": "water monthly", "msgnumber": "1"}'
                    eval: value.strip().split(' ')
                    on_change:
                    - sh..water_1(sh..self()[0])
                    - sh..water_2(sh..self()[1])
                    - sh..water_3(sh..self()[2])
                    - sh..water_4(sh..self()[3])
                    - sh..water_5(sh..self()[4])
                    - sh..water_6(sh..self()[5])
                    - sh..water_7(sh..self()[6])
                    - sh..water_8(sh..self()[7])
                    - sh..water_9(sh..self()[8])
                    - sh..water_10(sh..self()[9])
                    - sh..water_11(sh..self()[10])
                    - sh..water_12(sh..self()[11])
                    - sh..water_13(sh..self()[12])
                    - sh..water_14(sh..self()[13])
                    - sh..water_15(sh..self()[14])
                    - sh..water_16(sh..self()[15])
                    - sh..water_17(sh..self()[16])
                    - sh..water_18(sh..self()[17])
                    - sh..water_19(sh..self()[18])
                    - sh..water_20(sh..self()[19])
                    - sh..water_21(sh..self()[20])
                    - sh..water_22(sh..self()[21])
                    - sh..water_23(sh..self()[22])
                    - sh..water_24(sh..self()[23])
                    - sh..water_25(sh..self()[24])
                    - sh..water_26(sh..self()[25])
                    - sh..water_27(sh..self()[26])
                    - sh..water_28(sh..self()[27])
                    - sh..water_29(sh..self()[28]) if len(sh..self()) > 28 else -1
                    - sh..water_30(sh..self()[29]) if len(sh..self()) > 29 else -1
                    - sh..water_31(sh..self()[30]) if len(sh..self()) > 30 else -1
                    
                water_monthly:
                    type: num
                    visu_acl: r
                    database: Init
                    crontab: 
                    - "55 23 28-31 * = 1"                    
                    eval: max(0, sh...water.water_1()) + max(0, sh...water.water_2()) + max(0, sh...water.water_3()) + max(0, sh...water.water_4()) + max(0, sh...water.water_5()) + max(0, sh...water.water_6()) + max(0, sh...water.water_7()) + max(0, sh...water.water_8()) + max(0, sh...water.water_9()) + max(0, sh...water.water_10()) + max(0, sh...water.water_11()) + max(0, sh...water.water_12()) + max(0, sh...water.water_13()) + max(0, sh...water.water_14())
                    
                    
```

### logic.yaml

No logic related stuff implemented.

## Methods

No methods provided currently.
