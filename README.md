# Install
このプログラムはモジュールPretty Midiに依存しています。GitHubからPretty Midiを[ダウンロード](https://github.com/craffel/pretty-midi)し、`pretty_midi`というフォルダをこのディレクトリにコピーしてください。

# Get Started
## MIDIファイルから音符列を読み取る
第1チャンネルに単音から構成されるメロディーラインを記述したMIDIファイルを読み込みます。
```python
from typing import List
from pretty_midi import Note, PrettyMIDI

score = PrettyMIDI("../samples/永遠のひとつ-サビ.mid")
instrument = score.instruments[0]
notes:List[Note] = instrument.notes
N = len(notes)
print(f"ノート数は{N} 運指は{5**N:.03e}通り")
```

```
ノート数は60 運指は8.674e+41通り
```
## コスト行列モデルを起動する
コスト行列とは、指番号$i$から指番号$j$へ移動する際のコストを$(i,j)$成分に記述した$5\times 5$行列であり、これは、現在の音`current`、次の音`next`、現在の音から次の音までの時間`delta_time`に依存します。

基底クラスは`CostmatModel`で、実装として以下があります。
* `StandardModel` : `current`から`next`の距離と$i$から$j$の距離の差に比例して大きくなるというごく単純なコスト行列を表します。
* `Myamya1Model` : Mya-Myaの経験則に基づいて定めたコスト行列を表します。
```python
from costmatmodel import CostmatModel
from myamya1model import Myamya1Model

costmatmodel:CostmatModel = Myamya1Model()
```

## コスト計算機を起動する
`CostCalculator`を用いて、特定の音符列に対応するコスト行列を全て生成します。
```python
from costcalculator import CostCalculator

cc = CostCalculator(costmatmodel, notes)
print(cc.costmat_s)
```
```
(array([[0.5, 0.9, 1. , 1. , 1. ],
        [0. , 0.5, 1. , 1. , 1. ],
        [0.1, 0. , 0.5, 1. , 1. ],
        [0.2, 0.6, 0. , 0.5, 1. ],
        [0.8, 0.8, 0.7, 0. , 0.9]]),
 array([[0.6, 0.4, 0.7, 1. , 1. ],
        [0.1, 0.6, 0.9, 1. , 1. ],
        [0. , 0.1, 0.6, 1. , 1. ],
        [0.1, 0. , 0.3, 0.5, 1. ],
        [0.4, 0.7, 0. , 0.4, 0.8]]),
 array([[0.7, 0.1, 0. , 0. , 0.3],
        [0.6, 0.7, 0.2, 0.1, 0. ],
        [0.9, 0.9, 0.6, 0.4, 0. ],
        [1. , 1. , 1. , 0.6, 0.4],
        [1. , 1. , 1. , 1. , 0.8]]),
 array([[0.5, 0.9, 1. , 1. , 1. ],
        [0. , 0.5, 1. , 1. , 1. ],
        [0.1, 0. , 0.5, 1. , 1. ],
        [0.2, 0.6, 0. , 0.5, 1. ],
        [0.8, 0.8, 0.7, 0. , 0.9]]),
 array([[0.5, 0. , 0.1, 0.2, 0.8],
        [0.9, 0.5, 0. , 0.6, 0.8],
        [1. , 1. , 0.5, 0. , 0.7],
        [1. , 1. , 1. , 0.5, 0. ],
        [1. , 1. , 1. , 1. , 0.9]]),
...
 array([[0. , 0.1, 0.3, 0.4, 0.8],
        [0.2, 0. , 0.5, 0.4, 0.7],
        [0.4, 0.3, 0. , 0.3, 0.7],
        [0.5, 0.6, 0.6, 0. , 0.5],
        [0.8, 0.9, 0.8, 0.5, 0. ]]))
```
例えば、`cc.costmat_s[0]`は、音符`notes[0]`から音符`notes[1]`に移る際のコスト行列です。

## ランダムに運指を作成し、コストを求める。
音符に割り振る指の番号は`0,1,2,3,4`のいずれかで、それぞれ親指、人差し指、中指、薬指、小指を表します。以下のコードでは、運指をランダムに生成し、`CostCalculator#get_total_cost`にて、コストの合計を計算します。
```python
import random

fa = random.choices(range(5),k=N) #指番号の整数列
print(fa)
total_cost = cc.get_total_cost(fa)
print(total_cost)
```
```
[1, 4, 2, 1, 4, 3, 0, 3, 3, 4, 4, 3, 0, 0, 3, 1, 1, 0, 0, 4, 4, 2, 0, 2, 3, 4, 2, 0, 3, 3, 2, 3, 1, 4, 1, 0, 0, 4, 0, 2, 0, 0, 1, 3, 1, 0, 0, 2, 1, 0, 4, 2, 4, 4, 3, 4, 2, 0, 1, 3]
45.2
```

# 遺伝アルゴリズムでの運指の最適化
ここでは、コストの合計がより小さくなるような運指=指番号の整数列を求めるために、遺伝アルゴリズムを使用します。

ハイパーパラメーター(個体数、世代数、親の数)をそれぞれ以下のように定めます。
```python
num_individual = 5000
num_generation = 100
num_parent = 100
```
単交叉及び一定確率での突然変異を行う、子個体の生成メソッドを作ります。また、突然変異の発生確率のスケジューラも作ります。
```python
from typing import List, Sequence
from copy import copy

def make_child(p1: Sequence[int], p2: Sequence[int], mr: float = 0.2) -> List[int]:
    assert len(p1) == len(p2)
    size = len(p1)
    max_index = size-1
    i = random.randint(0, max_index)
    j = random.randint(i, max_index)
    c = copy(p1)
    c[i:j] = p2[i:j]

    while random.random() < mr:
        k = random.randint(0, max_index)
        c[k] = random.randint(0, 4)
    return c


def mr_scheduler(progress: float) -> float:
    return max(0.0, 0.7*(1.0-progress)**1.2)
```
ここでの「個体」とは、1つの運指=指番号列を指します。複数の個体のコストをそれぞれ計算するメソッドも作っておきます。
```python
from typing import Tuple

def get_cost_s(cc:CostCalculator,individual_s:Sequence[Sequence[int]])->Tuple[float]:
    return tuple(cc.get_total_cost(fa) for fa in individual_s)
```
以下が最適化ループです。
```python
from tqdm import tqdm
from numpy import mean, std, argsort, argmin

# 初期世代の個体を生成し、コストを計算する。
individual_s = tuple(
    random.choices(range(5), k=N)
    for _ in range(num_individual)
)
cost_s = get_cost_s(cc, individual_s)

# 世代別のコストの平均値と標準偏差
mean_cost_history = [mean(cost_s)]
std_cost_history = [std(cost_s)]

for generation in tqdm(tuple(range(num_generation))):
    # コストの低い個体から順に親とする。
    parent_index_s = argsort(cost_s)[:num_parent]
    parent_s = tuple(individual_s[i] for i in parent_index_s)
    mr = mr_scheduler(generation/num_generation)
    # 次の世代の個体を生成し、コストを計算する。
    individual_s = tuple(
        make_child(
            random.choice(parent_s), random.choice(parent_s),
            mr=mr
        )
        for _ in range(num_individual)
    )
    cost_s = get_cost_s(cc, individual_s)
    mean_cost_history.append(mean(cost_s))
    std_cost_history.append(std(cost_s))
```
得られた最適解を表示します。見やすくするため、指番号は1~5にシフトしています。
```python
from pandas import DataFrame
from pretty_midi import note_number_to_name

best_index = argmin(cost_s)
best_cost = cost_s[best_index]
best_fa = individual_s[best_index]
print("Cost=", best_cost)
best_fa_table = DataFrame({
    "N.": (note_number_to_name(n.pitch) for n in notes),
    "F.": (f+1 for f in best_fa)
})
print(best_fa_table)
```
```
Cost= 2.0000000000000004
     N.  F.
0   A#5   4
1    A5   3
2    F5   1
3   A#5   4
4    A5   3
5   A#5   4
6   A#5   4
7    A5   3
8   A#5   4
9    A5   3
10   G5   2
...
```