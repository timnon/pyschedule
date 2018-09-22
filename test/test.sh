#ls *.py | sed 's/$/ --test/' | xargs -n 1 -P 3 python
ls *.py | xargs -I % sh -c 'python % --test'
