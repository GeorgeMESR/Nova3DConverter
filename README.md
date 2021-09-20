# Nova3DConverter

ConvertToCWS.py
Код для конвертирования zip файла, создаваемого Chitubox, в CWS файл для принтера "Nova3D Elfin2 mono se"
Требует библиотеку Pillow

Настройка Chitubox
В Chitubox необходимо загрузить профиль принтера с необходимым разрешением и размерами печатной зоны (загружается с сайта производителя).  
Также нужно установить толщину слоя 'Layer Thickness'.

Slicing  в Chitubox
Стандартный Slicе. В качестве выходного формата выбираем ZIP. Chitubox создаст файл ZIP, в котором есть набор слоев в виде png файлов и run.gcode. В run.gcode есть заголовок с перечислением параметров притера,сам gcode остуствует. Необходимые параметры: ';layerHeight:', ';totalLayer:', ';resolutionX:' и ';resolutionY:'

Конвертирование в файл для печати на "Nova3D Elfin2 mono se"
Для конвертирования в файл понятный принтеру код создает файл с gcode, файл с slice.conf, конвертирует изображения слоев, объединив в один пиксель три идущих подряд пикселя и все это архивировует в zip, изменяя расширение на cws. Параметры печати взяты из cws, созданного программой LycheeSlicer и хранятся в директории gcode.  

1. Полученный zip файл помещаем в директорию 'In'.
2. В 10 строке присваиваем переменной 'fileName' название файла без расширения (.zip не надо).  
3. В 13 строке устанавливаем время засветки одного слоя config_printer['Layer Time'] в миллисекундах.
4. Запускаем скрипт. Внимание скрипт удалит все файлы из директорий 'Out/tmp' и 'Out/tmp1'. При начале работы скрипт выдаст параметры толщину слоя 'Layer Thickness' и общее число слоев 'Number of Slices', считанные из файла 'run.gcode'.  Затем проинформирует о конвертации каждого слоя. После окончания работы скрипта, в директории 'Out' появится файл 'fileName'.cws, в распакованном виде созданные файлы находятся в  директории 'Out/tmp1'.

Возможные проблемы - быстрое преобразование файлов работает только для исходных изображений слоя в формате grayscale. Возможно, при выключенном anti-aliasing формат будет BW, что потребует дополнительного конвертирования.

KicadPCBexp.py - Пока совсем не тестировался!!!
Код засветки фоторезиста (или фотополимера) для создания печатных плат.
Требует библиотеки Pillow и pcb-tools (https://pypi.org/project/pcb-tools/)

Входные файлы: Файлы в формате gerber для  нижнего и верхнего (или только одного) слоя, слоя разреза (размеров) платы, а также файл отверстий в формате gerber.
Имена файлов соответствуют выходным файлам kicad- выглядят как fileName+'-F_Cu.gbr', fileName+'-B_Cu.gbr', fileName+'-Edge_Cuts.gbr', fileName+'-PTH_d.drl'.
В случае другого формата имен необходимо редактировать строки 43-51.

Работа скрипта:
1. Файлы необходимо поместить в директорию 'In'
2. В 13 строке присваиваем переменной 'fileName' общую часть названия файла.   
3. В 14-16 строке выбираем печать необходимых слоев.
4. В 18-21 строке выбираем размер и необходимость накернения в верхнем слое.
5. В 23-25 строках устанавливаем время экспозиции платы, время показа размера платы для ее позиционирования и тип фоторезиста.
6. Запускаем код.
7. После работы в директории 'Out' получаем файл для запуска на принтере. Изображения слоев можно посмотреть в директории 'Out/tmp1', "несжатое" изображение preview.png

При запуске печати файла сначала 'Waiting' секунд  показывается "черный" прямоугольник с размерами платы, за это время необходимо успеть положить плату с нанесенным фоторезистом на стол принтера.
Затем включается изображение слоя принтера.

Если планируется двухслойная плата то в слое разреза платы (fileName+'-Edge_Cuts.gbr') необходимо кроме границ платы создать два дополнительных отверстия в пределах границ платы. После чего запустить скрипт с Layers='Both'. Вывести на печать нижний слой. Проявить фоторезист и затем просверлить два дополнительных отверстия. Затем запустить печать верхнего слоя. Сначала запустится изображение для позиционирования- на фоне черного прямоугольника (размер платы) появятся две ярких точки - отверстия из слоя Edge_Cuts. Необходимо успеть положить плату, так, чтобы эти точки совпали с дополнительными отверстиями. Через 'Waiting' секунд включится изображения верхнего слоя платы, для засветки фоторезиста.
Скрипт не тестировался, возможно не правильно включено зеркалирование слоев и совсем не проверялась печать негатива.
