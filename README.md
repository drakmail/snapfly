For now, project is under development. Post here any bugs you will find, and try to get the most recent version (maybe they're already fixed there).

На данный момент, проект находится в стадии развития и доработки кода, поэтому, большая просьба: если программа не запускается, или функционал не соответствует заявленному - возьмите последнюю версию из git, а если проблема есть и там, то пожалуйста напишите нам об этом!

## English description

SnapFly is a lightweight PyGTK menu which can be run as a daemon (in this case you can call the menu from any place on your desktop using snapfly-show) or as a standalone menu with a systray icon. The development began as a patchset for adeskmenu, but nowadays SnapFly is almost fully rewritten.

### Important changes:

* Menu regeneration without restarting (uses pyinotify for FS monitoring).
* Menu calling mechanism changed from sending SIGUSER1 signal to sending a dbus signal, which makes response faster and prevents 100% CPU usage.
* i18n (support for gettext for application-specific strings and system locale for desktop entries).
* Configurability, including custom menu entries and categories
OnlyShowIn section support (means DE-specific applications no longer show in different DE's).
* Reimplemented and/or optimized pretty much all the code

## Russian description
SnapFly - Легковесное GTK меню, которое можно запустить как в режиме демона (при этом его можно будет вызвать в любом месте экрана под курсором мыши без значка в трее) так и в обычном режиме, со значком в системном лотке. Является форком проекта adeskmenu.

### Список основных отличий:

* Автоматическая регенерация меню без перезапуска приложения (используя `pyinotify`).
* Механизм вызова меню изменен с посылки `SIGUSR1` сигнала на dbus-вызов (вследствие чего удалось значительно увеличить быстродействие и предотвратить 100% загрузку ЦП).
* Добавлена поддержка мультиязычности как для категорий (используя `gettext`), так и для самих `.desktop` файлов (используя текущий язык системы).
* Исправлен парсер и синтаксис конфигурационного файла пользовательского меню (добавление сторонних категорий и пунктов меню пользователем).
* Реализована настройка приложения с помощью конфигурационного файла - теперь параметры приложения можно изменять, не трогая исходный код. Также реализован парсер, который будет следить за правильностью его заполнения и оповещать, если какие-то переменные не верны. (если параметр указан неправильно, например, вместо `true` написано `123` - берется значение по-умолчанию для данной переменной)
* Реализован функционал `OnlyShowIn` `.desktop` файлов - теперь можно указать, какие приложения вы хотите видеть в меню, а какие нет (например можно выключить отображение GNOME/KDE приложений)
для показа меню в режиме 'демона' добавлен скрипт snapfly-show, дублирующий функционал убран из основного приложения.
и многое другое.

