#!/bin/sh
case $1 in
        "Limburger")
                        $pythonfile = newspapers/limburger.py
                        $username = 'nel@nelruigrok.nl'
                        $password = x6waDjy
                        $articleset = Limburger;;
        "Spitsnieuws")
                        $pythonfile = newspapers/spitsnieuws.py
                        $username = ''
                        $password = ''
                        $articleset = Spitsnieuws;;
        "Telegraaf")
                        $pythonfile =  newspapers/telegraaf.py
                        $username = 'nel@nelruigrok.nl'
                        $password = nieuwsmonitor
                        $articleset = Telegraaf;;
        "Trouw")
                        $pythonfile =  newspapers/trouw.py
                        $username = 'p.c.ruigrok@uva.nl'
                        $password = nieuwsmonitor
                        $articleset = Trouw;;
        "Algemeen Dagblad")
                        $pythonfile =  newspapers/ad.py
                        $username = martijn.bastiaan@gmail.com
                        $password = PKTAXkHE
                        $articleset = 'Algemeen Dagblad';;
        "NRC Handelsblad")
                        $pythonfile =  newspapers/nrchandelsblad.py
                        $username = nieuwsmonitor
                        $password = nieuwsmonitor
                        $articleset = 'NRC Handelsblad';;
        "Nrc Next")
                        $pythonfile = newspapers/nrcnext.py
                        $username = nelruigrok
                        $password = nieuwsmonitor
                        $articleset = 'NRC Next';;
        "Volkskrant")
			echo blaat
                        $pythonfile = newspapers/volkskrant.py
                        $username = nruigrok@hotmail.com
                        $password = 5ut5jujr
                        $articleset = Volkskrant;;
	*)
                        $pythonfile = '' 
                        $username = ''
                        $password = ''
                        $articleset = '';;
esac

nohup python $pythonfile 258 $2 $username $password --$articleset $articleset > logs/$1.out 2> logs/$1.err < /dev/null &

