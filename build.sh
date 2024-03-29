#!/bin/bash
rm -rf *.so
echo "Programming language..."
command=$(ls|grep my_player)
py=$([[ $command =~ (^|[[:space:]])"my_player.py"($|[[:space:]]) ]] && echo 'yes' || echo 'no')
py3=$([[ $command =~ (^|[[:space:]])"my_player3.py"($|[[:space:]]) ]] && echo 'yes' || echo 'no')

if [ "$py" == "yes" ]; then
	cmd="python my_player.py"
	echo "PY"
elif [ "$py3" == "yes" ]; then
    cmd="python3 my_player3.py"
	echo "PY3"
else
    echo "ERROR: INVALID FILENAME"
	exit 1
fi
echo ""

prefix="./"
opponent=("random_player") #i.e. opponent
surfix=".py"

# play funcion
play()
{    
    echo Clean up... >&2
    if [ -f "input.txt" ]; then
        rm input.txt
    fi
    if [ -f "output.txt" ]; then
        rm output.txt
    fi
    cp $prefix/init/input.txt ./input.txt

    echo Start Playing... >&2

	moves=0
	while true
	do
        if [ -f "output.txt" ]; then
	        rm output.txt
	    fi

        echo "Black makes move..." >&2
		eval "$1" >&2
		let moves+=1

		python $prefix/host.py -m $moves -v True >&2
		rst=$?

		if [[ "$rst" != "0" ]]; then
			break
		fi

        if [ -f "output.txt" ]; then
	        rm output.txt
	    fi

		echo "White makes move..." >&2
		eval "$2" >&2
		let moves+=1

		python $prefix/host.py -m $moves -v True >&2
		rst=$?

		if [[ "$rst" != "0" ]]; then
			break
		fi
	done

	echo $rst
}

play_time=2

### start playing ###

echo ""
echo $(date)

for i in {0..0} # 1 opponent
do
    echo ""
    echo ==Playing with ${opponent[i]}==
    echo $(date)
    ta_cmd="python $prefix${opponent[i]}$surfix"
    black_win_time=0
    white_win_time=0
    black_tie=0
    white_tie=0
    for (( round=1; round<=$play_time; round+=2 )) 
    do
        # opponent takes Black
        echo "=====Round $round====="
        echo Black:opponent White:You 
        winner=$(play "$ta_cmd" "$cmd")
        if [[ "$winner" = "2" ]]; then
            echo 'White(You) win!'
            let white_win_time+=1
        elif [[ "$winner" = "0" ]]; then
            echo Tie.
            let white_tie+=1
        else
            echo 'White(You) lose.'
        fi

        # Student takes Black
        echo "=====Round $((round+1))====="
        echo Black:You White:opponent
        winner=$(play "$cmd" "$ta_cmd")
        if [[ "$winner" = "1" ]]; then
            echo 'Black(You) win!'
            let black_win_time+=1
        elif [[ "$winner" = "0" ]]; then
            echo Tie.
            let black_tie+=1
        else
            echo 'Black(You) lose.'
        fi
    done


    echo =====Summary=====  
    echo "You play as Black Player | Win: $black_win_time | Lose: $((play_time/2-black_win_time-black_tie)) | Tie: $black_tie"
    echo "You play as White Player | Win: $white_win_time | Lose: $((play_time/2-white_win_time-black_tie)) | Tie: $white_tie"
done

if [ -f "input.txt" ]; then
    rm input.txt
fi
if [ -f "output.txt" ]; then
    rm output.txt
fi
                                      
if [ -e "my_player.class" ]; then
    rm *.class
fi
if [ -e "exe" ]; then
    rm exe
fi
if [ -e "__pycache__" ]; then
    rm -rf __pycache__
fi
        
        
echo ""
echo Mission Completed.
echo $(date)