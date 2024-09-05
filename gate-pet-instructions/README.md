# Tutorial: Utilizando o Gate para Simulações PET

## 1. Preparação do Ambiente

### Opção 1 - Docker
**Download da Imagem do Gate**: Acesse o Docker Hub e escolha a imagem desejada (exemplo: `9.2-docker`).

```bash
docker pull opengatecollaboration/gate:9.2-docker
```

Criação de Volume: Crie um volume para armazenar os dados gerados.

```bash
docker volume create gate_data
```
## 2. Execução de um Macro
Rodando o Macro: Utilize o seguinte comando para executar um macro no Docker.

```bash
docker run -it -v $PWD:/APP -v gate_data:/data opengatecollaboration/gate:9.2-docker ./main.mac 
```


### Opção 2 - snap
[Instruções](https://snapcraft.io/install/gate/ubuntu)


Iniciando o Gate: No terminal, digite:
```bash
Gate
/control/execute ./<Nome_DO_Arquivo_Mac>
```

## Instalando o Root
Root é uma aplicação capaz de fazer a análise de dados do arquivo de saída das simulações;
Instale por esse método:

https://snapcraft.io/install/root-framework/ubuntu


    
Exemplo de Arquivo Macro: Você pode testar um exemplo disponível no repositório oficial:
https://github.com/OpenGATE/GateContrib/tree/v9.0/imaging/PET


# Introdução ao Macro do Gate
O macro (arquivos .mac) são responsáveis por definir as configurações das simulações:
qual tipo (PET, SPECT, Radioterapia), diferentes sistemas, geometria, arquivo de output, etc.
Nesses exemplos, daremos enfoque nos sistemas PET: CylindricalPET, Ecat, CPet, OPet.

## 1. Arquivos externos para configuração
Certifique-se de copiar os arquivos GateMaterials.db, Verbose.mac e MoveVisu.mac.
Você pode encontrá-los no repositório oficial:
https://github.com/OpenGATE/GateContrib/tree/v9.0/imaging/PET
Ou nesse repositório que escrevo o README.md


## 2. Estrutura do Script Gate

1. Escolha a geometria e o material do mundo.
2. Escolha um sistema - aqui, abordaremos os sistemas PET.
3. De acordo com a Tabela 1.1, defina as geometrias desse sistema.
4. Adicione detectores sensíveis (cristais e fantomas).
5. Defina o digitizer.
6. Defina o formato dos dados a serem coletados.

## 3. Instruções iniciais
### 3.1 Observações sobre geometria

Após a escolha do sistema, devemos nos atentar as suas geometrias e cofnigurações:

Forma Geométrica dos Componentes: Ao configurar uma simulação no GATE, é importante considerar a forma geométrica dos diferentes componentes do sistema, como o gantry (estrutura que segura o detector), os setores, os "buckets" (compartimentos), e os materiais detectores (como os cintiladores). Cada um desses componentes tem uma geometria específica que deve ser corretamente representada na simulação.

Níveis de Volume Físico: A simulação é estruturada em níveis hierárquicos de volumes físicos, onde cada nível deve estar contido dentro do volume do nível superior. Por exemplo, um cristal detector estaria contido dentro de um "bucket", que por sua vez estaria dentro de um setor, e assim por diante.

Número de Níveis: O número de níveis na hierarquia da geometria deve ser definido e seguir as especificações estabelecidas, possivelmente listadas em uma tabela (como a mencionada Tabela 1.1). Isso é crucial para garantir que a simulação seja precisa e esteja de acordo com os requisitos do sistema sendo simulado.

Numeração dos Volumes Sensíveis: A numeração dos volumes sensíveis (aqueles que detectam radiação, como cristais) é determinada pelo sistema escolhido e precisa estar em conformidade com um formato de saída específico. Isso significa que, dependendo da configuração do sistema, a forma como os detectores são numerados pode variar.

Limitação de Componentes por Nível: O número máximo de componentes (como cristais) em cada nível é limitado pelo formato de saída da simulação, uma vez que isso pode ser restrito pelo número de bits disponíveis para numerar os cristais. Isso se refere à capacidade de armazenamento de dados e como as informações sobre os cristais são codificadas para a saída da simulação.

### 3.2 Conectando geometrias com o sistema

Definir a Estrutura Geométrica: Antes de conectar a geometria a um sistema, você precisa definir a estrutura geométrica. Isso significa especificar os diferentes volumes e componentes, garantindo que eles sigam as restrições geométricas mencionadas anteriormente (como o fato de que um volume deve estar completamente contido no volume do nível superior).

Anexar a Geometria ao Sistema: Depois de definir a geometria, você precisa associá-la ao sistema que está sendo simulado. Isso é feito usando o comando attach, onde você especifica o nome do sistema (SystemName), o nível da hierarquia geométrica (Level), e o nome do volume que você definiu (UserVolumeName). Isso permite que a simulação saiba como a geometria deve ser integrada ao sistema simulado.

SystemName: Refere-se ao sistema específico que você está simulando (por exemplo, um scanner de tomografia, PET, etc.).
Level: Corresponde a um nível específico na hierarquia da geometria (como um setor, bucket, ou cristal).
UserVolumeName: É o nome que você atribuiu a um volume específico ao definir a geometria.


```bash 

### DEFININDO UMA GEOMETRIA
#	LSO layer
/gate/crystal/daughters/name                  LSO
/gate/crystal/daughters/insert                box
/gate/LSO/placement/setTranslation            -0.75 0.0 0.0 cm
/gate/LSO/geometry/setXLength                 15 mm
/gate/LSO/geometry/setYLength                 3.0 mm
/gate/LSO/geometry/setZLength                 3.8 mm
/gate/LSO/setMaterial                         LSO
/gate/LSO/vis/setColor                        red


#	A T T A C H    S Y S T E M 
/gate/systems/cylindricalPET/layer0/attach    LSO
```
Veja que o a conexão segue um padrão:

```bash 
gate/systems/component/level/attach USERVOLUMENAME
```

Observe também que, ao definir uma nova geometria, devemos dizer qual a geometria pai:

```bash
/gate/crystal/daughters/name                  LSO
/gate/crystal/daughters/insert                box
```


### Table
| System         | Components and Shape | Available Outputs                                                       |
|----------------|----------------------|--------------------------------------------------------------------------|
| OPET           | rsector, box          | Basic Output: ASCII, ROOT and Raw. Specific: LMF                         |
|                | module, box           |                                                                          |
|                | submodule, box        |                                                                          |
|                | crystal, box          |                                                                          |
|                | layer, wedge          |                                                                          |
| ecatAccel      | block, box            | Basic Output: ASCII, ROOT and Raw. Specific: SINOGRAM or ECAT7           |
|                | crystal               |                                                                          |
| ecat           | block, box            | Basic Output: ASCII, ROOT and Raw. Specific: SINOGRAM or ECAT7           |
|                | crystal               |                                                                          |
| cylindricalPET | rsector, box          | Basic Output: ASCII, ROOT and Raw. Specific: LMF                         |
|                | module, box           |                                                                          |
|                | submodule, box        |                                                                          |
|                | crystal, box          |                                                                          |
|                | layer, box            |                                                                          |
| CPET           | sector, cylinder      | Basic Output: ASCII, ROOT                                                |
|                | cassette, cylinder    |                                                                          |
|                | module, box           |                                                                          |
|                | crystal, box          |                                                                          |
|                | layer, box            |                                                                          |


## 3. Definição de Sistemas
### CylindricalPET

#### Introdução
CylindricalPET é um sistema PET que pode descrever a maioria dos scanners PET para pequenos animais. A principal característica do CylindricalPET é a possibilidade de registrar dados de saída no formato List Mode Format (LMF) desenvolvido pela Crystal Clear Collaboration. Uma descrição completa do LMF pode ser encontrada em Saída LMF.


#### Geometria
Um CylindricalPET é baseado em uma geometria cilíndrica e consiste em 5 níveis hierárquicos, do nível mais alto ao mais baixo, conforme definido abaixo:

world: O CylindricalPET é definido como um cilindro dentro do mundo, com um raio interno diferente de zero.

rsector (profundidade=1): É definido como uma caixa, repetida com um repetidor de anel dentro do CylindricalPET.

module (profundidade=2): É uma caixa dentro do rsector. É repetido por um repetidor de array cúbico sem repetição em X (repeatNumberX = 1). Este nível é opcional.

submodule (profundidade=3): É uma caixa dentro do module. É repetido por um repetidor de array cúbico sem repetição em X (repeatNumberX = 1). Este nível é opcional.

crystal (profundidade=4): É uma caixa dentro do submodule. É repetido por um repetidor de array cúbico sem repetição em X (repeatNumberX = 1).

layer (profundidade=5): É uma (ou várias) caixas dispostas radialmente dentro do crystal. Um repetidor não deve ser usado para layers, mas elas devem ser construídas uma por uma no macro. A layer deve ser configurada como um detector sensível com o comando macro (que veremos mais a frente)

```bash
/attachCrystalSD
```

As palavras em negrito são dedicadas. Veja também as palavras-chave na Tabela 1.2.

O material da(s) layer(s) deve ser o material do detector, por exemplo, LSO ou BGO + GSO para um sistema de dupla camada phoswich. Os materiais de outros níveis (crystals, submodules, modules, rsectors, cylindricalPET) podem ser qualquer outro.

IMPORTANTE: A visualização deve ajudar você a construir esta geometria sem sobreposições. O GATE realiza um teste para detectar sobreposição de volumes, mas com uma precisão limitada. Este teste é realizado no final da inicialização do GATE (ver Introdução):

```bash
/run/initialize
/geometry/test/recursive_test
```

Os usuários devem verificar cuidadosamente que os volumes não são maiores do que o volume pai em que estão incluídos.

Um exemplo de definição de um scanner PET seguindo a estrutura do sistema CylindricalPET é dado abaixo. A definição do scanner deve ser realizada no início do macro, antes das inicializações:

```bash # W O R L D
/gate/world/geometry/setXLength 40 cm
/gate/world/geometry/setYLength 40. cm
/gate/world/geometry/setZLength 40. cm

# M O U S E
/gate/world/daughters/name mouse
/gate/world/daughters/insert cylinder
/gate/mouse/setMaterial Water
/gate/mouse/vis/setColor red
/gate/mouse/geometry/setRmax 18.5 mm
/gate/mouse/geometry/setRmin 0. mm
/gate/mouse/geometry/setHeight 68. mm

# C Y L I N D R I C A L
/gate/world/daughters/name cylindricalPET
/gate/world/daughters/insert cylinder
/gate/cylindricalPET/setMaterial Water
/gate/cylindricalPET/geometry/setRmax 145 mm
/gate/cylindricalPET/geometry/setRmin 130 mm
/gate/cylindricalPET/geometry/setHeight 80 mm
/gate/cylindricalPET/vis/forceWireframe

# R S E C T O R
/gate/cylindricalPET/daughters/name rsector
/gate/cylindricalPET/daughters/insert box
/gate/rsector/placement/setTranslation 135 0 0 mm
/gate/rsector/geometry/setXLength 10. mm
/gate/rsector/geometry/setYLength 19. mm
/gate/rsector/geometry/setZLength 76.6 mm
/gate/rsector/setMaterial Water
/gate/rsector/vis/forceWireframe

# M O D U L E
/gate/rsector/daughters/name module
/gate/rsector/daughters/insert box
/gate/module/geometry/setXLength 10. mm
/gate/module/geometry/setYLength 19. mm
/gate/module/geometry/setZLength 19. mm
/gate/module/setMaterial Water
/gate/module/vis/forceWireframe
/gate/module/vis/setColor gray

# C R Y S T A L
/gate/module/daughters/name crystal
/gate/module/daughters/insert box
/gate/crystal/geometry/setXLength 10. mm
/gate/crystal/geometry/setYLength 2.2 mm
/gate/crystal/geometry/setZLength 2.2 mm
/gate/crystal/setMaterial Water
/gate/crystal/vis/forceWireframe
/gate/crystal/vis/setColor magenta

# L A Y E R
/gate/crystal/daughters/name LSO
/gate/crystal/daughters/insert box
/gate/LSO/geometry/setXLength 10. mm
/gate/LSO/geometry/setYLength 2.2 mm
/gate/LSO/geometry/setZLength 2.2 mm
/gate/LSO/placement/setTranslation 0 0 0 mm
/gate/LSO/setMaterial LSO
/gate/LSO/vis/setColor yellow

# R E P E A T C R Y S T A L
/gate/crystal/repeaters/insert cubicArray
/gate/crystal/cubicArray/setRepeatNumberX 1
/gate/crystal/cubicArray/setRepeatNumberY 8
/gate/crystal/cubicArray/setRepeatNumberZ 8
/gate/crystal/cubicArray/setRepeatVector 10. 2.4 2.4 mm

# R E P E A T M O D U L E
/gate/module/repeaters/insert cubicArray
/gate/module/cubicArray/setRepeatNumberZ 4
/gate/module/cubicArray/setRepeatVector 0. 0. 19.2 mm

# R E P E A T R S E C T O R
/gate/rsector/repeaters/insert ring
/gate/rsector/ring/setRepeatNumber 42

# A T T A C H S Y S T E M
/gate/systems/cylindricalPET/rsector/attach rsector
/gate/systems/cylindricalPET/module/attach module
/gate/systems/cylindricalPET/crystal/attach crystal
/gate/systems/cylindricalPET/layer0/attach LSO

# A T T A C H L A Y E R SD
/gate/LSO/attachCrystalSD
/gate/mouse/attachPhantomSD
```

### CPET


#### Introdução
Este sistema foi definido para a simulação de um scanner similar ao CPET (C-PET Plus, Philips Medical Systems, Países Baixos), com um anel de cristal de NaI em formato curvo. Para este scanner, um único nível além do nível do sistema é suficiente para descrever a hierarquia de volumes.
Mais informações:
https://tech.snmjournals.org/content/28/1/23

Este sistema tem a particularidade de possuir componentes de sector (que anexam cristais nele) em forma cilíndrica, baseados no formato de cilindro, enquanto que, em outros sistemas, esses componentes geralmente são boxes.

![Cristal único do CPet](https://opengate.readthedocs.io/en/v9.2/_images/OnesectorCPET.jpg)

Cristal único do CPet

![Cristais após repetição](https://opengate.readthedocs.io/en/v9.2/_images/FullsectorCPET.jpg)

Cristais após repetição


#### Geometria


#### Módulos de Saída


#### Escrevendo Macro
Abaixo está descrito um exemplo de código apropriado para modelar um scanner com um anel de cristal de NaI com formato curvo:

```bash
# BASE = SISTEMA CPET
/gate/world/daughters/name CPET
/gate/world/daughters/insert cylinder
/gate/CPET/setMaterial Air
/gate/CPET/geometry/setRmax 60 cm
/gate/CPET/geometry/setRmin 0.0 cm
/gate/CPET/geometry/setHeight 35.0 cm
/gate/CPET/vis/forceWireframe

# PRIMEIRO NÍVEL = CRISTAL
/gate/CPET/daughters/name crystal
/gate/CPET/daughters/insert cylinder
/gate/crystal/geometry/setRmax 47.5 cm
/gate/crystal/geometry/setRmin 45.0 cm
/gate/crystal/geometry/setHeight 25.6 cm
/gate/crystal/geometry/setPhiStart 0 deg
/gate/crystal/geometry/setDeltaPhi 60 deg

# REPETIR O SETOR CURVO EM TODO O ANEL
/gate/crystal/repeaters/insert ring
/gate/crystal/ring/setRepeatNumber 6

# O VOLUME DO CRISTAL É FEITO DE NAI
/gate/crystal/setMaterial NaI
/gate/crystal/vis/setColor green
```

O objeto cristal é então anexado ao seu componente correspondente no sistema CPET (nível 1: o nível do setor para o sistema CPET - veja a seção anterior para detalhes)


```bash
/gate/systems/CPET/sector/attach crystal
```
Os cristais são configurados como detectores sensíveis: 

```bash
/gate/crystal/attachCrystalSD
```

### Sistema Ecat

#### Introdução
Versão simplificada do cylindricalPET.
Modela scanners PET da família ECAT (CPS Innovations).
Baseado no princípio dos detectores em blocos:
Bloco: Matriz de cristais (tipicamente 8x8).
Fotomultiplicadores: Tipicamente 4.
Geometria: Anular, formando detectores multi-anéis.

#### Geometria
Níveis Hierárquicos:
Base: Detector inteiro.
Bloco: Conjunto de cristais.
Cristal: Elementos individuais dentro do bloco.

#### Módulos de Saída
Padrão de saída de dados: ASCII, root.
Específicos do Ecat: Formatos de sinograma (sinogram, ecat7).
Exemplo de Uso:
Estrutura de Código para Scanner de 4 Anéis de Blocos:

#### Escrevendo Macro

Define o sistema como volume filho do mundo.
Forma de anel para incluir todos os detectores.

```bash 
/gate/world/daughters/name ecat
/gate/world/daughters/insert cylinder
/gate/ecat/setMaterial Air
/gate/ecat/geometry/setRmax 442.0 mm
/gate/ecat/geometry/setRmin 412.0 mm
/gate/ecat/geometry/setHeight 155.2 mm
/gate/ecat/setTranslation 0.0 0.0 0.0 mm
```

Bloco:
Tamanho e Posição: Configurado dentro da base do ecat.
Geometria: Paralelepípedo retangular.

``` bash 
/gate/ecat/daughters/name block
/gate/ecat/daughters/insert box
/gate/block/placement/setTranslation 427.0 0.0 0.0 mm
/gate/block/geometry/setXLength 30.0 mm
/gate/block/geometry/setYLength 35.8 mm
/gate/block/geometry/setZLength 38.7 mm
/gate/block/setMaterial Air
```

Cristal:
Tamanho e Posição: Configurado dentro do bloco.
Geometria: Caixa, centrada no bloco.
Material: BGO (Bismuth Germanate).
```bash 
/gate/block/daughters/name crystal
/gate/block/daughters/insert box
/gate/crystal/placement/setTranslation 0.0 0.0 0.0 mm
/gate/crystal/geometry/setXLength 30.0 mm
/gate/crystal/geometry/setYLength 4.4 mm
/gate/crystal/geometry/setZLength 4.75 mm
/gate/crystal/setMaterial BGO
```


Matriz de Cristais:
Repetição: Definido para criar uma matriz de cristais no bloco.
Dimensões: 8x8.
```bash 
/gate/crystal/repeaters/insert cubicArray
/gate/crystal/cubicArray/setRepeatNumberX 1
/gate/crystal/cubicArray/setRepeatNumberY 8
/gate/crystal/cubicArray/setRepeatNumberZ 8
/gate/crystal/cubicArray/setRepeatVector 0. 4.45 4.80 mm
```

Anéis:
Repetição: Define o número de blocos por anel e número de anéis.
```bash /gate/block/repeaters/insert linear
/gate/block/linear/setRepeatNumber 4
/gate/block/linear/setRepeatVector 0. 0. 38.8 mm
/gate/block/repeaters/insert ring

## A alinha abaixo repete o bloco dentro do anel
/gate/block/ring/setRepeatNumber 72
```

Resultado: Scanner de 4 anéis de blocos, totalizando 32 anéis de cristais;
Cada anel terá 576 cristais (72*8)


Finalização:
Anexação: Blocos e cristais são anexados aos seus componentes correspondentes no sistema ecat.
```bash 
systems/ecat/block/attach block
systems/ecat/crystal/attach crystal
```
Detecção: Cristais são configurados como detectores sensíveis.
```bash 
/gate/crystal/attachCrystalSD
```

Digitalizador: Pode ser o mesmo do sistema cylindricalPET.

## 4. Anexando detectores sensíveis

### Introdução
Após adicionar escrever o modelo para o scanner, o próximo passo é anexar detectores sensíveis a volumes e fantomas.
Esses detectores sensíveis irão retornar as informações de interação de uma partícula, usando informações dos passos que ocorreram ao longo do caminho da partícula.


### crystalSD

O crystalSD é usado para guardar informações de interação dentro de volumes que pertençam ao scanner, como cristais: deposição de energia, posição das interações, origem da partícula, tipo de interação, etc.

Primeiramente, devemos anexar as geometrias ao sistema:


```bash 
#	A T T A C H    S Y S T E M 
/gate/systems/cylindricalPET/rsector/attach   head
/gate/systems/cylindricalPET/module/attach    block
/gate/systems/cylindricalPET/crystal/attach   crystal
/gate/systems/cylindricalPET/layer0/attach    LSO
/gate/systems/cylindricalPET/layer1/attach    BGO
```

Posteriormente, anexamos detectores as geometrias:

```bash 
#	A T T A C H    C R Y S T A L  SD

/gate/LSO/attachCrystalSD
/gate/BGO/attachCrystalSD
```

### phantomSD

Da mesma forma, podemos obter informações de um fantoma utilizando o attachPhantomSD


```bash 
#=====================================================
#  P H A N T O M
#=====================================================

#/gate/world/daughters/name                    phantom
#/gate/world/daughters/insert                  box

#/gate/phantom/geometry/setXLength             10 cm
#/gate/phantom/geometry/setYLength             10 cm
#/gate/phantom/geometry/setZLength             10 cm
#/gate/phantom/setMaterial                     Water
#/gate/phantom/vis/forceSolid
#/gate/phantom/vis/setColor                    blue

#/gate/phantom/attachPhantomSD

```


## 5. Definindo Digitizer
O digitizer é um módulo que processa os dados gerados pelos detectores, a partir de interações físicas e simula a eletrônica responsável por processar sinais, uma vez que outros processos alteram o output final e indica a saída real.
Adder Module: Soma os sinais de diferentes detectores.
Blurring Module: Aplica um desfoque nos dados para simular a dispersão de radiação.

Ler mais em: https://opengate.readthedocs.io/en/v9.2/digitizer_and_detector_modeling.html

```bash 

#=====================================================
#   D I G I T I Z E R: DETECTOR ELECTRONIC RESPONSE
#===================================================== 

/gate/digitizer/Singles/insert                        adder
/gate/digitizer/Singles/insert                        readout
/gate/digitizer/Singles/readout/setDepth              1

/gate/digitizer/Singles/insert                        blurring
/gate/digitizer/Singles/blurring/setResolution        0.26
/gate/digitizer/Singles/blurring/setEnergyOfReference 511. keV

/gate/digitizer/Singles/insert                        thresholder
/gate/digitizer/Singles/thresholder/setThreshold      350. keV
/gate/digitizer/Singles/insert                        upholder
/gate/digitizer/Singles/upholder/setUphold            650. keV
```
## 6. Concidências

O coincidence sorter em GATE identifica eventos de coincidência ao procurar pares de singles que ocorrem dentro de uma janela de coincidência. Existem dois métodos principais para isso:

Método 1: Quando um single é detectado, ele abre uma janela de coincidência, buscando outro single que ocorra dentro do tempo dessa janela. Enquanto a janela estiver aberta, nenhum outro single pode abrir uma nova janela.

Método 2: Cada single abre sua própria janela de coincidência e uma operação lógica OR é aplicada entre todas as janelas abertas para encontrar coincidências. Esse método pode identificar mais coincidências em comparação com o primeiro, mas é experimental e pode conter bugs não reportados.

Além disso, o coincidence sorter tem a capacidade de evitar coincidências entre partículas que foram espalhadas entre blocos adjacentes, usando um critério de proximidade. Esse critério, por padrão, aceita coincidências apenas se a diferença entre os números dos blocos for maior ou igual a dois, mas pode ser ajustado.

Coincidências Aleatórias
Cada single tem um ID de evento que identifica de qual decaimento ele se originou. Se dois singles com diferentes IDs formam uma coincidência, essa é considerada uma coincidência aleatória. Para estimar o número de coincidências aleatórias, pode-se usar uma janela de coincidência atrasada, onde uma segunda janela é aberta com um atraso suficiente para garantir que os singles sejam de decaimentos diferentes.

Coincidências Múltiplas
Quando mais de dois singles são encontrados em coincidência, GATE oferece nove regras diferentes para processar esses casos. Dependendo da regra escolhida, o sistema pode decidir se mantém ou descarta as coincidências múltiplas. Se nenhuma regra for especificada, a regra padrão usada é "keepIfAllAreGoods", que mantém a coincidência se todos os pares de singles forem bons.

Configuração do Coincidence Sorter
O usuário pode configurar a janela de coincidência, a diferença mínima entre setores para aceitar coincidências, o tipo de método para encontrar coincidências (método 1 ou 2), e a política para coincidências múltiplas usando comandos específicos no GATE.

Processamento e Filtragem de Coincidências
Após a identificação das coincidências, GATE permite aplicar filtros para simular perdas de contagem que podem ocorrer devido a limitações na aquisição, como tempo morto ou capacidade de buffer. Também é possível combinar diferentes tipos de coincidências (como prompts e delayed) em uma única linha de coincidência para processamento conjunto.

Exemplo:
```bash 
#=====================================================
#	C O I N C I D E N C E    S O R T E R
#===================================================== 

/gate/digitizer/Coincidences/setWindow          10. ns

/gate/digitizer/name                            delay
/gate/digitizer/insert                          coincidenceSorter
/gate/digitizer/delay/setWindow                 10. ns
/gate/digitizer/delay/setOffset                 500. ns
```

## 8. Configurações de medição
Finalizando o script macro, devemos definir os tempos de aquisição e dar o comando para realizar a aquisição (startDAQ)


```bash 
#=====================================================
#   M E A S U R E M E N T   S E T T I N G S   
#=====================================================

/gate/application/setTimeSlice   1 s
/gate/application/setTimeStart   0 s
/gate/application/setTimeStop    6 s

/gate/application/startDAQ
```

## 7. Output
Usualmente, utilizamos o root como formato de output, uma vez que possui a ferramenta para análise de dados também em Python.

```bash
/gate/output/root/enable
/gate/output/root/setFileName YourFileName
```

### Acesso a análise de dados
Após a configuração do root (ver seção de configuração de ambiente) você pode verificar os dados que retornam da simulação a partir de algum script Python, C++ (onde você tem acesso a todos os dados da simulação) ou para uma rápida verificação, utilizar o TBrowser, uma janela do Root onde você consegue criar gráficos e verificar os dados de output.

Na pasta onde o arquivo root foi criado, digite:

```bash 
root
YourFileName.root
TBrowser t
```
