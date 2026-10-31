# 小米手环 10 Pro / 3.101.043 Hook 点对照表

本表对应 Veposed 的 `xiaomi-band-10-pro-3.101.043` 适配表。模块使用名称，不需要写固件地址。AP SHA-256：`519307675665e4866d722a8119a98589c397b614ac3294cb87bfc86de45756ec`。列出的入口已核对该 AP 的字节与调用链，设备验证仍为 `pending`。

固件验证同时检查每个有调用者过滤的返回 PC 是否紧随 Thumb `BL`，并检查它直接或经已支持的绝对跳转桩到达配置的原生入口。此检查不证明函数语义、线程静止或真机行为。

初始化会在读取状态槽之前检查表项中非零槽地址的对齐和平台内存范围，并拒绝只有第二调用者的配置；表项验证失败时不会留下部分目录。地址通过范围检查不代表指针内容一定有效，槽的生命周期仍需依据固件调用链验证。

| Hook 名称 | 对应功能与触发 | 约定 | 原生目标 | 作用范围与安装条件 | 证据 |
| --- | --- | --- | --- | --- | --- |
| `settings.about.os_version` | 设置 → 我的设备 → 关于本机：OS 版本显示值 | `void2` | `lvx_label_set_text` | 调用点 `0x0c54d3ea`，标签槽 `0x20111c48`；安装前关闭关于页面 | [os-version-043.json](../evidence/os-version-043.json) |
| `settings.about.os_version_size` | 关于本机：OS 值标签的宽高设置 | `void3` | `lv_obj_set_size` | 调用点 `0x0c54d7e6`，标签槽 `0x20111c48`；安装前关闭关于页面 | [about-os-size-043.json](../evidence/about-os-size-043.json) |
| `settings.about.device_type` | 关于本机：设备型号显示值 | `void2` | `lvx_label_set_text` | 调用点 `0x0c54d32e`，标签槽 `0x20111c38`；安装前关闭关于页面 | [about-fields-043.json](../evidence/about-fields-043.json) |
| `settings.about.system_version` | 关于本机：系统版本显示值 | `void2` | `lvx_label_set_text` | 调用点 `0x0c54d382`，标签槽 `0x20111c50`；安装前关闭关于页面 | [about-fields-043.json](../evidence/about-fields-043.json) |
| `settings.about.mac_address` | 关于本机：MAC 显示值 | `void2` | `lvx_label_set_text` | 调用点 `0x0c54d43e`，标签槽 `0x20111c40`；安装前关闭关于页面 | [about-fields-043.json](../evidence/about-fields-043.json) |
| `settings.about.serial_number` | 关于本机：序列号显示值 | `void2` | `lvx_label_set_text` | 调用点 `0x0c54d490`，标签槽 `0x20111c68`；安装前关闭关于页面 | [about-fields-043.json](../evidence/about-fields-043.json) |
| `settings.about.system_version_clickable` | 关于本机：为系统版本值添加可点击标志，可拦截这一步 | `void2` | `lv_obj_add_flag` | 调用点 `0x0c54d3a6`，标签槽 `0x20111c50`，标志 `2`；安装前关闭关于页面 | [about-interaction-043.json](../evidence/about-interaction-043.json) |
| `settings.display.auto_brightness_hint` | 亮度设置：自动亮度说明标签；页面创建及语言刷新时触发 | `void2` | `lvx_label_set_text` | 调用点 `0x0c55542a`、`0x0c55515c`，标签槽 `0x20112354`；页面根槽 `0x2011233c` 用于安装静止和分发时存活检查 | [display-brightness-hint-043.json](../evidence/display-brightness-hint-043.json) |
| `settings.display.brightness.auto_register` | 亮度设置：自动亮度控件事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c555284`；根槽 `0x2011233c`、状态槽 `0x20112350`；安装前关闭亮度页面 | [display-brightness-actions-043.json](../evidence/display-brightness-actions-043.json) |
| `settings.display.brightness.sunshine_register` | 亮度设置：阳光模式控件事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c5553d6`；根槽 `0x2011233c`、状态槽 `0x20112350`；安装前关闭亮度页面 | [display-brightness-actions-043.json](../evidence/display-brightness-actions-043.json) |
| `settings.display.brightness.manual_register` | 亮度设置：手动亮度入口事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c555310`；根槽 `0x2011233c`、状态槽 `0x20112350`；安装前关闭亮度页面 | [display-brightness-actions-043.json](../evidence/display-brightness-actions-043.json) |
| `settings.display.brightness.action_data` | 亮度设置：共用回调读取操作编号 | `word1` | `lv_event_get_user_data` | 调用点 `0x0c554f70`；根槽 `0x2011233c`、状态槽 `0x20112350`；安装前关闭亮度页面 | [display-brightness-actions-043.json](../evidence/display-brightness-actions-043.json) |
| `settings.dnd.info` | 勿扰与睡眠设置：勿扰模式说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0x0c559ac6`，页面根槽 `0x20112648`；安装前关闭该页面 | [dnd-sleep-settings-043.json](../evidence/dnd-sleep-settings-043.json) |
| `settings.sleep_mode.info` | 勿扰与睡眠设置：睡眠模式说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0x0c559b6c`，页面根槽 `0x20112648`；安装前关闭该页面 | [dnd-sleep-settings-043.json](../evidence/dnd-sleep-settings-043.json) |
| `settings.dnd.schedule_register` | 勿扰与睡眠设置：注册勿扰时间设置行回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c559a72`，页面根槽 `0x20112648`；安装前关闭该页面 | [dnd-sleep-settings-043.json](../evidence/dnd-sleep-settings-043.json) |
| `settings.sleep_mode.toggle_register` | 勿扰与睡眠设置：注册睡眠模式开关回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c559b18`，页面根槽 `0x20112648`；安装前关闭该页面 | [dnd-sleep-settings-043.json](../evidence/dnd-sleep-settings-043.json) |
| `settings.dnd.schedule_click_data` | 勿扰时间设置行回调：读取事件用户数据 | `word1` | `lv_event_get_user_data` | 调用点 `0x0c5599b4`，页面根槽 `0x20112648`；安装前关闭该页面 | [dnd-sleep-settings-043.json](../evidence/dnd-sleep-settings-043.json) |
| `settings.return_to_dial.selected_description` | 返回表盘设置：当前选中选项的说明文字，列表重建时触发 | `void2` | `lvx_label_set_text` | 调用点 `0x0c54e256`，页面根槽 `0x20111c90`；安装前关闭该设置页面 | [return-to-dial-043.json](../evidence/return-to-dial-043.json) |
| `settings.return_to_dial.selected_option` | 返回表盘设置：点击选项时读取将写入设置的选项编号，可替换返回值以改变实际选择 | `word1` | `lv_event_get_user_data` | 调用点 `0x0c54e38c`，页面根槽 `0x20111c90`；安装前关闭该设置页面 | [return-to-dial-option-043.json](../evidence/return-to-dial-option-043.json) |
| `settings.return_to_dial.event_code` | 返回表盘设置：回调读取事件代码，可改变是否进入点击处理分支 | `word1` | `lv_event_get_code` | 调用点 `0x0c54e37c`，页面根槽 `0x20111c90`；安装前关闭该设置页面 | [event-code-043.json](../evidence/event-code-043.json) |
| `settings.return_to_dial.option_register` | 返回表盘设置：注册选项行点击回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c54e1b8`，页面根槽 `0x20111c90`；安装前关闭该设置页面 | [return-to-dial-option-043.json](../evidence/return-to-dial-option-043.json) |
| `settings.connectivity.nfc.event_code` | 更多连接设置：NFC 开关回调读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0x0c551308`，页面根槽 `0x20111f88`；安装前关闭该页面 | [connectivity-nfc-043.json](../evidence/connectivity-nfc-043.json) |
| `settings.connectivity.nfc.click_data` | 更多连接设置：NFC 开关回调读取点击数据 | `word1` | `lv_event_get_user_data` | 调用点 `0x0c551316`，页面根槽 `0x20111f88`；安装前关闭该页面 | [connectivity-nfc-043.json](../evidence/connectivity-nfc-043.json) |
| `settings.connectivity.nfc.click_register` | 更多连接设置：注册 NFC 开关点击回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c5512d4`，页面根槽 `0x20111f88`；安装前关闭该页面 | [connectivity-nfc-043.json](../evidence/connectivity-nfc-043.json) |
| `settings.battery.estimate` | 电池设置：预计续航说明，页面创建及电池事件更新时触发 | `void2` | `lvx_label_set_text` | 调用点 `0x0c54eeb8`、`0x0c54f486`，标签槽 `0x20111d6c`；安装前关闭电池页面 | [battery-estimates-043.json](../evidence/battery-estimates-043.json) |
| `settings.battery.long_mode_estimate` | 电池设置：长续航开关下方的预计续航说明 | `void2` | `lvx_label_set_text` | 调用点 `0x0c54f08e`、`0x0c54f52c`，标签槽 `0x20111d74`；安装前关闭电池页面 | [battery-estimates-043.json](../evidence/battery-estimates-043.json) |
| `settings.battery.charge_indicator_source` | 电池设置：充电指示图标的资源设置调用 | `void2` | `lv_image_set_src` | 调用点 `0x0c54ec52`，页面根槽 `0x20111d5c`；安装前关闭电池页面 | [battery-indicator-043.json](../evidence/battery-indicator-043.json) |
| `settings.battery.long_mode_click_data` | 电池设置：长续航开关点击处理读取的事件数据，可改变该回调的分支 | `word1` | `lv_event_get_user_data` | 调用点 `0x0c54f750`，页面根槽 `0x20111d5c`；安装前关闭电池页面 | [battery-long-mode-click-043.json](../evidence/battery-long-mode-click-043.json) |
| `settings.battery.long_mode_register` | 电池设置：注册长续航开关点击回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c54efb8`，页面根槽 `0x20111d5c`；安装前关闭电池页面 | [battery-long-mode-click-043.json](../evidence/battery-long-mode-click-043.json) |
| `watchface.selection.preview_name` | 表盘选择：预览卡片创建时的名称文字 | `void2` | `lvx_label_set_text` | 调用点 `0x0c5f75c6`，状态槽 `0x2011999c`；安装前关闭表盘选择界面 | [watchface-selection-043.json](../evidence/watchface-selection-043.json) |
| `watchface.selection.hint` | 表盘选择：提示卡片文字 | `void2` | `lvx_label_set_text` | 调用点 `0x0c5f6b20`，状态槽 `0x2011999c`；安装前关闭表盘选择界面 | [watchface-selection-043.json](../evidence/watchface-selection-043.json) |
| `watchface.selection.tile_event_code` | 表盘选择：预览列表回调读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0x0c5f62ea`，状态槽 `0x2011999c`；安装前关闭表盘选择界面 | [watchface-selection-043.json](../evidence/watchface-selection-043.json) |
| `watchface.selection.drag_start_event_code` | 表盘选择：拖动起始回调读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0x0c5f849a`，状态槽 `0x2011999c`；安装前关闭表盘选择界面 | [watchface-selection-043.json](../evidence/watchface-selection-043.json) |
| `watchface.selection.drag_motion_event_code` | 表盘选择：拖动过程回调读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0x0c5f7f7a`，状态槽 `0x2011999c`；安装前关闭表盘选择界面 | [watchface-selection-043.json](../evidence/watchface-selection-043.json) |
| `watchface.selection.drag_position_text` | 表盘选择：进入拖动时的位置／总数文字 | `void2` | `lvx_label_set_text` | 调用点 `0x0c5f8576`，状态槽 `0x2011999c`；安装前关闭表盘选择界面 | [watchface-selection-043.json](../evidence/watchface-selection-043.json) |
| `watchface.dual_time.selected_index` | 表盘双时区选择：读取点击行的时区列表编号，可改变保存和发布的选项 | `word1` | `lv_event_get_user_data` | 调用点 `0x0c5f201a`，页面根槽 `0x20119740`；安装前关闭双时区选择页面 | [watchface-dual-time-043.json](../evidence/watchface-dual-time-043.json) |
| `watchface.dual_time.option_register` | 表盘双时区选择：创建或更新选项时注册点击回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c5f2192`、`0x0c5f22d0`，页面根槽 `0x20119740`；安装前关闭该页面 | [watchface-dual-time-043.json](../evidence/watchface-dual-time-043.json) |
| `watchface.sport_selection.item_data` | 表盘运动选择：分类或运动条目点击时读取条目数据指针 | `word1` | `lv_event_get_user_data` | 调用点 `0x0c5f54f6`；分类根槽 `0x201198a8`、运动根槽 `0x201198b8`；安装前关闭两个页面 | [watchface-sport-selection-043.json](../evidence/watchface-sport-selection-043.json) |
| `watchface.sport_selection.item_register` | 表盘运动选择：创建或更新分类、运动条目时注册点击回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c5f578a`、`0x0c5f56b2`；分类根槽 `0x201198a8`、运动根槽 `0x201198b8`；安装前关闭两个页面 | [watchface-sport-selection-043.json](../evidence/watchface-sport-selection-043.json) |
| `apps.mijia.scene.selected_index` | 米家场景列表：点击时读取待执行场景的索引 | `word1` | `lv_event_get_user_data` | 调用点 `0x0c5074c2`，页面根槽 `0x2010ff20`；安装前关闭米家场景页面 | [mijia-scene-selection-043.json](../evidence/mijia-scene-selection-043.json) |
| `apps.mijia.scene.register_create` | 米家场景列表：创建行时注册场景回调的两个分支 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c506f32`、`0x0c506fc2`，页面根槽 `0x2010ff20`；安装前关闭该页面 | [mijia-scene-selection-043.json](../evidence/mijia-scene-selection-043.json) |
| `apps.mijia.scene.register_update` | 米家场景列表：更新行时注册场景回调的两个分支 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c506cf4`、`0x0c506d7e`，页面根槽 `0x2010ff20`；安装前关闭该页面 | [mijia-scene-selection-043.json](../evidence/mijia-scene-selection-043.json) |
| `apps.sports.list_edit.event_code` | 运动列表编辑：读取完成、删除或标记操作的事件代码 | `word1` | `lv_event_get_code` | 调用点 `0x0c58f77e`，页面根槽 `0x20114970`；安装前关闭运动列表编辑页面 | [sports-list-edit-043.json](../evidence/sports-list-edit-043.json) |
| `apps.sports.list_edit.action_data` | 运动列表编辑：读取完成、删除或标记操作的数据编号 | `word1` | `lv_event_get_user_data` | 调用点 `0x0c58f788`，页面根槽 `0x20114970`；安装前关闭运动列表编辑页面 | [sports-list-edit-043.json](../evidence/sports-list-edit-043.json) |
| `apps.sports.list_edit.flag_register` | 运动列表编辑：注册标记按钮回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c58f436`，编辑数据槽 `0x20114978`；安装前关闭编辑页面 | [sports-list-edit-043.json](../evidence/sports-list-edit-043.json) |
| `apps.sports.list_edit.delete_register` | 运动列表编辑：注册删除按钮回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c58f442`，编辑数据槽 `0x20114978`；安装前关闭编辑页面 | [sports-list-edit-043.json](../evidence/sports-list-edit-043.json) |
| `apps.sports.list_edit.done_register` | 运动列表编辑：注册完成按钮回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c58f568`，编辑数据槽 `0x20114978`；安装前关闭编辑页面 | [sports-list-edit-043.json](../evidence/sports-list-edit-043.json) |
| `health.heart_rate.current_caption` | 心率主页面：显示已有读数时的“当前”状态文字 | `void2` | `lvx_label_set_text` | 调用点 `0x0c667606`，页面状态槽 `0x2011f99c`；安装前关闭心率页面 | [heart-rate-status-043.json](../evidence/heart-rate-status-043.json) |
| `health.heart_rate.measuring_caption` | 心率主页面：测量中状态文字 | `void2` | `lvx_label_set_text` | 调用点 `0x0c6670ce`、`0x0c66729e`，页面状态槽 `0x2011f99c`；安装前关闭心率页面 | [heart-rate-status-043.json](../evidence/heart-rate-status-043.json) |
| `health.heart_rate.timeout_caption` | 心率主页面：超时状态文字 | `void2` | `lvx_label_set_text` | 调用点 `0x0c665fc6`，页面状态槽 `0x2011f99c`；安装前关闭心率页面 | [heart-rate-status-043.json](../evidence/heart-rate-status-043.json) |
| `health.heart_rate.retry_caption` | 心率主页面：超时界面的重试文字 | `void2` | `lvx_label_set_text` | 调用点 `0x0c665fd4`，页面状态槽 `0x2011f99c`；安装前关闭心率页面 | [heart-rate-status-043.json](../evidence/heart-rate-status-043.json) |
| `health.heart_rate.action_id` | 心率应用：共用操作回调读取的导航编号 | `word1` | `lv_event_get_user_data` | 调用点 `0x0c66145a`；覆盖多个心率页面，无页面根槽过滤；安装前需手动关闭相关页面 | [heart-rate-actions-043.json](../evidence/heart-rate-actions-043.json) |
| `health.heart_rate.setting.option_search_limit` | 心率设置选项回调读取的选项搜索上界 | `word1` | `lv_event_get_user_data` | 调用点 `0x0c66862a`，状态槽 `0x2011fa08`；安装前关闭相关选项页面 | [heart-rate-settings-reminders-043.json](../evidence/heart-rate-settings-reminders-043.json) |
| `health.heart_rate.reminder.ignore_register` | 心率提醒界面注册“忽略”按钮回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c6698a6`，状态槽 `0x2011fa1c`；安装前关闭提醒界面 | [heart-rate-settings-reminders-043.json](../evidence/heart-rate-settings-reminders-043.json) |
| `health.heart_rate.reminder.dismiss_register` | 心率提醒界面注册“今日不再提醒”按钮回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0x0c66990e`，状态槽 `0x2011fa1c`；安装前关闭提醒界面 | [heart-rate-settings-reminders-043.json](../evidence/heart-rate-settings-reminders-043.json) |
| `health.heart_rate.reminder.dismiss_type` | “今日不再提醒”回调读取提醒类型 | `word1` | `lv_event_get_user_data` | 调用点 `0x0c669392`，状态槽 `0x2011fa1c`；安装前关闭提醒界面 | [heart-rate-settings-reminders-043.json](../evidence/heart-rate-settings-reminders-043.json) |
| `apps.timer.preset_unit` | 计时器：预设分钟数的单位文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4ffc7a`，状态槽 `0x2010fcc8`、根槽 `0x200d02ec`；安装前关闭对应页面 | [timer-weather-043.json](../evidence/timer-weather-043.json) |
| `apps.timer.recent_caption` | 计时器：最近使用区标题文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4ffcf4`，状态槽 `0x2010fcc8`、根槽 `0x200d02ec`；安装前关闭对应页面 | [timer-weather-043.json](../evidence/timer-weather-043.json) |
| `apps.weather.city.initial_icon` | 天气城市列表：新建城市项的初始天气图标 | `void2` | `lv_image_set_src` | 调用点 `0xc60f34a`，状态槽 `0x2011ad7c`；安装前关闭对应页面 | [timer-weather-043.json](../evidence/timer-weather-043.json) |
| `apps.weather.city.condition_icon` | 天气城市列表：按城市天气刷新或使用缺省图标 | `void2` | `lv_image_set_src` | 调用点 `0xc60f5cc`、`0xc60f73e`，状态槽 `0x2011ad7c`；安装前关闭对应页面 | [timer-weather-043.json](../evidence/timer-weather-043.json) |
| `apps.weather.city.location_icon` | 天气城市列表：定位城市标志图标 | `void2` | `lv_image_set_src` | 调用点 `0xc60f978`、`0xc60f9b6`，状态槽 `0x2011ad7c`；安装前关闭对应页面 | [timer-weather-043.json](../evidence/timer-weather-043.json) |
| `apps.timer.done.close_register` | 计时结束提示页：注册关闭按钮回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4ff07c`，提示页根槽 `0x2010fc8c`；安装前关闭提示页 | [timer-done-actions-043.json](../evidence/timer-done-actions-043.json) |
| `apps.timer.done.restart_register` | 计时结束提示页：注册重新开始按钮回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4ff0fa`，提示页根槽 `0x2010fc8c`；安装前关闭提示页 | [timer-done-actions-043.json](../evidence/timer-done-actions-043.json) |
| `apps.timer.done.close_event_code` | 计时结束提示页：关闭按钮读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc4fef60`，提示页根槽 `0x2010fc8c`；安装前关闭提示页 | [timer-done-actions-043.json](../evidence/timer-done-actions-043.json) |
| `apps.timer.done.restart_event_code` | 计时结束提示页：重新开始按钮读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc4feed2`，提示页根槽 `0x2010fc8c`；安装前关闭提示页 | [timer-done-actions-043.json](../evidence/timer-done-actions-043.json) |
| `apps.timer.custom.hours_register` | 自定义计时器：注册小时选择回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc50162e`、`0xc501672`，状态槽 `0x2010fdb8`；安装前关闭自定义计时器页面 | [timer-custom-actions-043.json](../evidence/timer-custom-actions-043.json) |
| `apps.timer.custom.minutes_register` | 自定义计时器：注册分钟选择回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc501680`、`0xc50168e`，状态槽 `0x2010fdb8`；安装前关闭自定义计时器页面 | [timer-custom-actions-043.json](../evidence/timer-custom-actions-043.json) |
| `apps.timer.custom.seconds_register` | 自定义计时器：注册秒选择回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc50169c`、`0xc5016aa`，状态槽 `0x2010fdb8`；安装前关闭自定义计时器页面 | [timer-custom-actions-043.json](../evidence/timer-custom-actions-043.json) |
| `apps.timer.custom.start_register` | 自定义计时器：注册开始按钮回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc501708`，状态槽 `0x2010fdb8`；安装前关闭自定义计时器页面 | [timer-custom-actions-043.json](../evidence/timer-custom-actions-043.json) |
| `apps.timer.custom.hours_event_code` | 自定义计时器：小时选择回调读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc500d7c`，状态槽 `0x2010fdb8`；安装前关闭自定义计时器页面 | [timer-custom-actions-043.json](../evidence/timer-custom-actions-043.json) |
| `apps.timer.custom.minutes_event_code` | 自定义计时器：分钟选择回调读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc500e40`，状态槽 `0x2010fdb8`；安装前关闭自定义计时器页面 | [timer-custom-actions-043.json](../evidence/timer-custom-actions-043.json) |
| `apps.timer.custom.seconds_event_code` | 自定义计时器：秒选择回调读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc500f04`，状态槽 `0x2010fdb8`；安装前关闭自定义计时器页面 | [timer-custom-actions-043.json](../evidence/timer-custom-actions-043.json) |
| `apps.timer.custom.hours_caption` | 自定义计时器：选择小时后的提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc500cf2`，状态槽 `0x2010fdb8`；安装前关闭自定义计时器页面 | [timer-custom-actions-043.json](../evidence/timer-custom-actions-043.json) |
| `apps.timer.custom.minutes_caption` | 自定义计时器：选择分钟后的提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc500db6`，状态槽 `0x2010fdb8`；安装前关闭自定义计时器页面 | [timer-custom-actions-043.json](../evidence/timer-custom-actions-043.json) |
| `apps.timer.custom.seconds_caption` | 自定义计时器：选择秒后的提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc500e7a`，状态槽 `0x2010fdb8`；安装前关闭自定义计时器页面 | [timer-custom-actions-043.json](../evidence/timer-custom-actions-043.json) |
| `apps.alarm.list.row_register` | 闹钟列表：注册条目行回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc53dcc0`、`0xc53dd9c`，状态槽 `0x20111570`；安装前关闭闹钟主页面 | [alarm-list-actions-043.json](../evidence/alarm-list-actions-043.json) |
| `apps.alarm.list.switch_register` | 闹钟列表：注册启用开关回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc53dd12`、`0xc53dde4`，状态槽 `0x20111570`；安装前关闭闹钟主页面 | [alarm-list-actions-043.json](../evidence/alarm-list-actions-043.json) |
| `apps.alarm.list.row_event_code` | 闹钟列表：读取闹钟条目点击事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc53d690`，状态槽 `0x20111570`；安装前关闭闹钟主页面 | [alarm-list-actions-043.json](../evidence/alarm-list-actions-043.json) |
| `apps.alarm.list.row_index` | 闹钟列表：读取待编辑的闹钟索引 | `word1` | `lv_event_get_user_data` | 调用点 `0xc53d6a0`，状态槽 `0x20111570`；安装前关闭闹钟主页面 | [alarm-list-actions-043.json](../evidence/alarm-list-actions-043.json) |
| `apps.alarm.list.switch_event_code` | 闹钟列表：读取启用开关的状态变化事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc53d41c`，状态槽 `0x20111570`；安装前关闭闹钟主页面 | [alarm-list-actions-043.json](../evidence/alarm-list-actions-043.json) |
| `apps.alarm.list.switch_index` | 闹钟列表：读取启用开关对应的闹钟索引 | `word1` | `lv_event_get_user_data` | 调用点 `0xc53d40c`，状态槽 `0x20111570`；安装前关闭闹钟主页面 | [alarm-list-actions-043.json](../evidence/alarm-list-actions-043.json) |
| `apps.alarm.repeat.weekday_register` | 闹钟自定义重复：注册星期行和选择控件回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc53c3c2`、`0xc53c41a`，页面根槽 `0x200d1390`；安装前关闭自定义重复页面 | [alarm-repeat-actions-043.json](../evidence/alarm-repeat-actions-043.json) |
| `apps.alarm.repeat.weekday_index` | 闹钟自定义重复：读取星期索引 | `word1` | `lv_event_get_user_data` | 调用点 `0xc53c432`，页面根槽 `0x200d1390`；安装前关闭自定义重复页面 | [alarm-repeat-actions-043.json](../evidence/alarm-repeat-actions-043.json) |
| `apps.alarm.repeat.event_code` | 闹钟自定义重复：读取星期点击事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc53c43c`，页面根槽 `0x200d1390`；安装前关闭自定义重复页面 | [alarm-repeat-actions-043.json](../evidence/alarm-repeat-actions-043.json) |
| `apps.alarm.repeat.weekday_caption` | 闹钟自定义重复：星期行标题文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc53c3f8`，页面根槽 `0x200d1390`；安装前关闭自定义重复页面 | [alarm-repeat-actions-043.json](../evidence/alarm-repeat-actions-043.json) |
| `system.launcher.icon.click_register` | 应用列表：注册应用图标点击回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc51782e`，应用列表根槽 `0x201102f4`；安装前关闭应用列表 | [launcher-interactions-043.json](../evidence/launcher-interactions-043.json) |
| `system.launcher.icon.app_id` | 应用列表：点击图标读取应用 ID | `word1` | `lv_event_get_user_data` | 调用点 `0xc517422`，应用列表根槽 `0x201102f4`；安装前关闭应用列表 | [launcher-interactions-043.json](../evidence/launcher-interactions-043.json) |
| `system.launcher.icon.source` | 应用列表：设置应用图标资源 | `void2` | `lv_image_set_src` | 调用点 `0xc5177d2`，应用列表根槽 `0x201102f4`；安装前关闭应用列表 | [launcher-interactions-043.json](../evidence/launcher-interactions-043.json) |
| `system.launcher.icon.caption` | 应用列表：设置图标标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc51788c`、`0xc5179a6`，应用列表根槽 `0x201102f4`；安装前关闭应用列表 | [launcher-interactions-043.json](../evidence/launcher-interactions-043.json) |
| `system.launcher.layout.register` | 应用列表：注册切换布局按钮回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc517b24`，应用列表根槽 `0x201102f4`；安装前关闭应用列表 | [launcher-interactions-043.json](../evidence/launcher-interactions-043.json) |
| `system.launcher.layout.event_code` | 应用列表：切换布局按钮读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc517622`，应用列表根槽 `0x201102f4`；安装前关闭应用列表 | [launcher-interactions-043.json](../evidence/launcher-interactions-043.json) |
| `apps.media.control.register_other` | 媒体控制：注册其他控制项回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc51f534`、`0xc51fb20`，媒体页面状态槽 `0x20110918`；安装前关闭媒体页面 | [media-control-actions-043.json](../evidence/media-control-actions-043.json) |
| `apps.media.control.register_23` | 媒体控制：注册编号 2、3 控制项回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc51f918`、`0xc51fd0c`，媒体页面状态槽 `0x20110918`；安装前关闭媒体页面 | [media-control-actions-043.json](../evidence/media-control-actions-043.json) |
| `apps.media.control.register_4` | 媒体控制：注册编号 4 控制项回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc51f960`、`0xc51fc88`，媒体页面状态槽 `0x20110918`；安装前关闭媒体页面 | [media-control-actions-043.json](../evidence/media-control-actions-043.json) |
| `apps.media.control.event_code` | 媒体控制：读取共用回调事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc51dae0`，媒体页面状态槽 `0x20110918`；安装前关闭媒体页面 | [media-control-actions-043.json](../evidence/media-control-actions-043.json) |
| `apps.media.control.current_target` | 媒体控制：读取触发事件的控件对象 | `word1` | `lv_event_current_target` | 调用点 `0xc51daea`，媒体页面状态槽 `0x20110918`；安装前关闭媒体页面 | [media-control-actions-043.json](../evidence/media-control-actions-043.json) |
| `system.notifications.group.item_register` | 通知聚合：创建或更新消息行时注册点击回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc525dee`、`0xc525c4e`，聚合页面根槽 `0x20110e88`；安装前关闭该页面 | [notification-group-actions-043.json](../evidence/notification-group-actions-043.json) |
| `system.notifications.group.clear_register` | 通知聚合：注册清除全部按钮回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc525e38`，聚合页面根槽 `0x20110e88`；安装前关闭该页面 | [notification-group-actions-043.json](../evidence/notification-group-actions-043.json) |
| `system.notifications.group.app_name` | 通知聚合：更新消息行的应用名 | `void2` | `lvx_label_set_text` | 调用点 `0xc525c6e`，聚合页面根槽 `0x20110e88`；安装前关闭该页面 | [notification-group-actions-043.json](../evidence/notification-group-actions-043.json) |
| `system.notifications.group.title` | 通知聚合：更新消息行的标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc525c80`，聚合页面根槽 `0x20110e88`；安装前关闭该页面 | [notification-group-actions-043.json](../evidence/notification-group-actions-043.json) |
| `system.notifications.group.content` | 通知聚合：更新消息行的内容 | `void2` | `lvx_label_set_text` | 调用点 `0xc525c92`，聚合页面根槽 `0x20110e88`；安装前关闭该页面 | [notification-group-actions-043.json](../evidence/notification-group-actions-043.json) |
| `system.notifications.group.time` | 通知聚合：更新消息行的时间文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc525cb4`，聚合页面根槽 `0x20110e88`；安装前关闭该页面 | [notification-group-actions-043.json](../evidence/notification-group-actions-043.json) |
| `system.notifications.group.clear_caption` | 通知聚合：更新清除全部按钮文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc525cdc`，聚合页面根槽 `0x20110e88`；安装前关闭该页面 | [notification-group-actions-043.json](../evidence/notification-group-actions-043.json) |
| `apps.camera.shutter.press_register` | 遥控相机：注册快门按下事件 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc54bac4`、`0xc54baf4`，页面根槽 `0x20111bc8`；安装前关闭遥控相机 | [remote-camera-actions-043.json](../evidence/remote-camera-actions-043.json) |
| `apps.camera.shutter.release_register` | 遥控相机：注册快门释放事件 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc54bad0`、`0xc54bb00`，页面根槽 `0x20111bc8`；安装前关闭遥控相机 | [remote-camera-actions-043.json](../evidence/remote-camera-actions-043.json) |
| `apps.camera.shutter.event_code` | 遥控相机：快门回调读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc54b542`，页面根槽 `0x20111bc8`；安装前关闭遥控相机 | [remote-camera-actions-043.json](../evidence/remote-camera-actions-043.json) |
| `apps.camera.shutter.pressed_icon` | 遥控相机：设置快门按下状态图标 | `void2` | `lv_image_set_src` | 调用点 `0xc54b59e`，页面根槽 `0x20111bc8`；安装前关闭遥控相机 | [remote-camera-actions-043.json](../evidence/remote-camera-actions-043.json) |
| `apps.camera.shutter.released_icon` | 遥控相机：设置快门释放状态图标 | `void2` | `lv_image_set_src` | 调用点 `0xc54b56c`，页面根槽 `0x20111bc8`；安装前关闭遥控相机 | [remote-camera-actions-043.json](../evidence/remote-camera-actions-043.json) |
| `apps.camera.delay.register` | 遥控相机：注册倒计时选项回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc54bb5a`，页面根槽 `0x20111bc8`；安装前关闭遥控相机 | [remote-camera-actions-043.json](../evidence/remote-camera-actions-043.json) |
| `apps.camera.delay.event_code` | 遥控相机：倒计时选项读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc54b252`，页面根槽 `0x20111bc8`；安装前关闭遥控相机 | [remote-camera-actions-043.json](../evidence/remote-camera-actions-043.json) |
| `apps.camera.hint.text` | 遥控相机：打开手机相机提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc54ae32`，页面根槽 `0x20111bc8`；安装前关闭遥控相机 | [remote-camera-actions-043.json](../evidence/remote-camera-actions-043.json) |
| `apps.camera.hint.register` | 遥控相机：注册提示页面按钮回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc54ae9a`，页面根槽 `0x20111bc8`；安装前关闭遥控相机 | [remote-camera-actions-043.json](../evidence/remote-camera-actions-043.json) |
| `apps.camera.hint.event_code` | 遥控相机：提示页面按钮读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc54b1c4`，页面根槽 `0x20111bc8`；安装前关闭遥控相机 | [remote-camera-actions-043.json](../evidence/remote-camera-actions-043.json) |
| `settings.sound.dnd_register` | 声音设置：注册勿扰设置行回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc56f9ca`，状态槽 `0x20113448`；安装前关闭对应设置页面 | [sound-vibration-actions-043.json](../evidence/sound-vibration-actions-043.json) |
| `settings.sound.vibration_toggle_register` | 声音设置：注册振动开关回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc56fa56`，状态槽 `0x20113448`；安装前关闭对应设置页面 | [sound-vibration-actions-043.json](../evidence/sound-vibration-actions-043.json) |
| `settings.sound.vibration_mode_register` | 声音设置：注册振动模式行回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc56faa0`，状态槽 `0x20113448`；安装前关闭对应设置页面 | [sound-vibration-actions-043.json](../evidence/sound-vibration-actions-043.json) |
| `settings.sound.action_id` | 声音设置：读取点击操作编号 | `word1` | `lv_event_get_user_data` | 调用点 `0xc56f2ca`，状态槽 `0x20113448`；安装前关闭对应设置页面 | [sound-vibration-actions-043.json](../evidence/sound-vibration-actions-043.json) |
| `settings.vibration.selection_register` | 振动模式：注册标准／增强选项回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc570092`，状态槽 `0x20113488`；安装前关闭对应设置页面 | [sound-vibration-actions-043.json](../evidence/sound-vibration-actions-043.json) |
| `settings.vibration.selection_data` | 振动模式：读取选择回调数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc56fd32`，状态槽 `0x20113488`；安装前关闭对应设置页面 | [sound-vibration-actions-043.json](../evidence/sound-vibration-actions-043.json) |
| `settings.vibration.selection_target` | 振动模式：读取选择控件 | `word1` | `lv_event_current_target` | 调用点 `0xc56fd3a`，状态槽 `0x20113488`；安装前关闭对应设置页面 | [sound-vibration-actions-043.json](../evidence/sound-vibration-actions-043.json) |
| `settings.vibration.confirm_event_code` | 振动模式：增强提示回调读取事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc56fe56`，状态槽 `0x20113488`；安装前关闭对应设置页面 | [sound-vibration-actions-043.json](../evidence/sound-vibration-actions-043.json) |
| `settings.notification_center.focus_register` | 通知中心设置：注册专注通知开关回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc568530`、`0xc5687a8`，页面状态槽 `0x2011314c`；安装前关闭对应设置页面 | [center-settings-actions-043.json](../evidence/center-settings-actions-043.json) |
| `settings.notification_center.focus_data` | 通知中心设置：读取专注通知开关数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc5683dc`，页面状态槽 `0x2011314c`；安装前关闭对应设置页面 | [center-settings-actions-043.json](../evidence/center-settings-actions-043.json) |
| `settings.notification_center.focus_hint` | 通知中心设置：专注通知说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc568566`、`0xc5687f2`，页面状态槽 `0x2011314c`；安装前关闭对应设置页面 | [center-settings-actions-043.json](../evidence/center-settings-actions-043.json) |
| `settings.control_center.toggle_register` | 控制中心设置：注册融合设备中心开关 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc55190e`，页面状态槽 `0x20111fbc`；安装前关闭对应设置页面 | [center-settings-actions-043.json](../evidence/center-settings-actions-043.json) |
| `settings.control_center.hint` | 控制中心设置：融合设备中心说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc551946`，页面状态槽 `0x20111fbc`；安装前关闭对应设置页面 | [center-settings-actions-043.json](../evidence/center-settings-actions-043.json) |
| `settings.about.ui_create` | 设置：关于本机：UI 创建回调 | `word3` | `settings_about_ui_create` | 指针槽 `0x200d207c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.about.ui_destroy` | 设置：关于本机：UI 销毁回调 | `void1` | `settings_about_ui_destroy` | 指针槽 `0x200d2094`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.brightness.ui_create` | 设置：亮度：UI 创建回调 | `word3` | `settings_display_brightness_ui_create` | 指针槽 `0x200d2898`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.brightness.ui_destroy` | 设置：亮度：UI 销毁回调 | `void1` | `settings_display_brightness_ui_destroy` | 指针槽 `0x200d28b0`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.dnd.ui_create` | 设置：勿扰与睡眠：UI 创建回调 | `word3` | `settings_dnd_ui_create` | 指针槽 `0x200d2b68`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.dnd.ui_destroy` | 设置：勿扰与睡眠：UI 销毁回调 | `void1` | `settings_dnd_ui_destroy` | 指针槽 `0x200d2b80`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.battery.ui_create` | 设置：电池：UI 创建回调 | `word3` | `settings_battery_ui_create` | 指针槽 `0x200d2338`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.battery.ui_destroy` | 设置：电池：UI 销毁回调 | `void1` | `settings_battery_ui_destroy` | 指针槽 `0x200d2350`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.connectivity.ui_create` | 设置：更多连接：UI 创建回调 | `word3` | `settings_connectivity_ui_create` | 指针槽 `0x200d2518`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.connectivity.ui_destroy` | 设置：更多连接：UI 销毁回调 | `void1` | `settings_connectivity_ui_destroy` | 指针槽 `0x200d2530`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.heart_rate.ui_create` | 心率主页面：UI 创建回调 | `word3` | `health_heart_rate_ui_create` | 指针槽 `0x200dbecc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.heart_rate.ui_destroy` | 心率主页面：UI 销毁回调 | `void1` | `health_heart_rate_ui_destroy` | 指针槽 `0x200dbee4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `watchface.dual_time.ui_create` | 表盘双时区：UI 创建回调 | `word3` | `watchface_dual_time_ui_create` | 指针槽 `0x200d8cac`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `watchface.dual_time.ui_destroy` | 表盘双时区：UI 销毁回调 | `void1` | `watchface_dual_time_ui_destroy` | 指针槽 `0x200d8cc4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.mijia.scene.ui_create` | 米家场景：UI 创建回调 | `word3` | `apps_mijia_scene_ui_create` | 指针槽 `0x200d05d0`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.mijia.scene.ui_destroy` | 米家场景：UI 销毁回调 | `void1` | `apps_mijia_scene_ui_destroy` | 指针槽 `0x200d05e8`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.timer.ui_create` | 计时器主页面：UI 创建回调 | `word3` | `apps_timer_ui_create` | 指针槽 `0x200d0308`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.timer.ui_destroy` | 计时器主页面：UI 销毁回调 | `void1` | `apps_timer_ui_destroy` | 指针槽 `0x200d0320`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.alarm.ui_create` | 闹钟主页面：UI 创建回调 | `word3` | `apps_alarm_ui_create` | 指针槽 `0x200d14e4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.alarm.ui_destroy` | 闹钟主页面：UI 销毁回调 | `void1` | `apps_alarm_ui_destroy` | 指针槽 `0x200d14fc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.weather.ui_create` | 天气主页面：UI 创建回调 | `word3` | `apps_weather_ui_create` | 指针槽 `0x200da430`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.weather.ui_destroy` | 天气主页面：UI 销毁回调 | `void1` | `apps_weather_ui_destroy` | 指针槽 `0x200da448`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.ui_create` | 睡眠主页面：UI 创建回调 | `word3` | `health_sleep_ui_create` | 指针槽 `0x200db1c4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.ui_destroy` | 睡眠主页面：UI 销毁回调 | `void1` | `health_sleep_ui_destroy` | 指针槽 `0x200db1dc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.oxygen.ui_create` | 血氧主页面：UI 创建回调 | `void3` | `health_oxygen_ui_create` | 指针槽 `0x200db520`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.oxygen.ui_destroy` | 血氧主页面：UI 销毁回调 | `void1` | `health_oxygen_ui_destroy` | 指针槽 `0x200db538`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `system.launcher.ui_create` | 应用列表主页面：UI 创建回调 | `word3` | `system_launcher_ui_create` | 指针槽 `0x200d0d58`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `system.launcher.ui_destroy` | 应用列表主页面：UI 销毁回调 | `void1` | `system_launcher_ui_destroy` | 指针槽 `0x200d0d70`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.list.ui_create` | 运动列表主页面：UI 创建回调 | `word3` | `sports_list_ui_create` | 指针槽 `0x200d5070`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.list.ui_destroy` | 运动列表主页面：UI 销毁回调 | `void1` | `sports_list_ui_destroy` | 指针槽 `0x200d5088`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.stress.ui_create` | 压力主页面：UI 创建回调 | `word3` | `health_stress_ui_create` | 指针槽 `0x200dae14`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.stress.ui_destroy` | 压力主页面：UI 销毁回调 | `void1` | `health_stress_ui_destroy` | 指针槽 `0x200dae2c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.breath.modes.register` | 模式列表：模式入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc629b5c`、`0xc629c74`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.mode_data` | 模式列表：读取选中模式 | `word1` | `lv_event_get_user_data` | 调用点 `0xc62a3aa`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.info_text` | 模式列表：说明提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc629bf2`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.start_register` | 模式页：开始入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc629d9a`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.start_text` | 模式页：开始提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc629e54`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.mode_bg` | 模式页：瑜伽或腹式背景 | `void2` | `lv_image_set_src` | 调用点 `0xc629dd2`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.box_bg` | 模式页：方形呼吸背景 | `void2` | `lv_image_set_src` | 调用点 `0xc629e74`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.buzz_bg` | 模式页：嗡鸣呼吸背景 | `void2` | `lv_image_set_src` | 调用点 `0xc629e7c`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.interrupted_text` | 结果页：中断提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc62a1e0`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.retry_register` | 结果页：重试入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc62a24e`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.result_done_register` | 结果页：确认入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc62a2aa`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.time_register` | 设置页：时长入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc62a4ce`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.explain_register` | 设置页：说明入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc62a51c`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.duration_text` | 时长页：分钟标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc62a6fa`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.duration_confirm` | 时长页：确认入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc62a892`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.action_data` | 训练页：读取动作数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc62af8a`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.session.stop_register` | 会话页：结束入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc62bd98`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.session.restart_register` | 会话页：重新开始入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc62bdd2`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.session.stop_text` | 会话页：结束文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc62be24`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.session.restart_text` | 会话页：重新开始文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc62be84`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.session.action_data` | 会话页：读取按钮动作数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc62bfda`，关闭对应页面后安装或卸载 | [breath-actions-043.json](../evidence/breath-actions-043.json) |
| `health.breath.ui_create` | 呼吸主页面：UI 创建回调 | `word3` | `health_breath_ui_create` | 指针槽 `0x200dac60`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.breath.ui_destroy` | 呼吸主页面：UI 销毁回调 | `void1` | `health_breath_ui_destroy` | 指针槽 `0x200dac78`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.heart_rate.settings.ui_create` | 心率设置页面：UI 创建回调 | `word3` | `health_heart_rate_settings_ui_create` | 指针槽 `0x200dc03c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.heart_rate.settings.ui_destroy` | 心率设置页面：UI 销毁回调 | `void1` | `health_heart_rate_settings_ui_destroy` | 指针槽 `0x200dc054`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.stress.settings.monitor_register` | 压力设置：监测开关回调注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc63358a`，关闭压力设置页面后安装或卸载 | [stress-settings-actions-043.json](../evidence/stress-settings-actions-043.json) |
| `health.stress.settings.relax_register` | 压力设置：放松提醒开关回调注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc633600`，关闭压力设置页面后安装或卸载 | [stress-settings-actions-043.json](../evidence/stress-settings-actions-043.json) |
| `health.stress.settings.relax_initial_hide` | 压力设置：初始化时隐藏放松提醒行 | `void2` | `lv_obj_add_flag` | 调用点 `0xc63356c`，关闭压力设置页面后安装或卸载 | [stress-settings-actions-043.json](../evidence/stress-settings-actions-043.json) |
| `health.stress.settings.relax_initial_show` | 压力设置：初始化时显示放松提醒行 | `void2` | `lv_obj_clear_flag` | 调用点 `0xc63362a`，关闭压力设置页面后安装或卸载 | [stress-settings-actions-043.json](../evidence/stress-settings-actions-043.json) |
| `health.stress.settings.relax_monitor_hide` | 压力设置：监测开关处理时隐藏提醒行 | `void2` | `lv_obj_add_flag` | 调用点 `0xc6338a8`，关闭压力设置页面后安装或卸载 | [stress-settings-actions-043.json](../evidence/stress-settings-actions-043.json) |
| `health.stress.settings.relax_refresh_hide` | 压力设置：设置事件刷新时隐藏提醒行 | `void2` | `lv_obj_add_flag` | 调用点 `0xc633688`，关闭压力设置页面后安装或卸载 | [stress-settings-actions-043.json](../evidence/stress-settings-actions-043.json) |
| `health.stress.settings.relax_refresh_show` | 压力设置：设置事件刷新时显示提醒行 | `void2` | `lv_obj_clear_flag` | 调用点 `0xc6336ae`，关闭压力设置页面后安装或卸载 | [stress-settings-actions-043.json](../evidence/stress-settings-actions-043.json) |
| `health.stress.settings.ui_create` | 压力设置页面：UI 创建回调 | `word3` | `health_stress_settings_ui_create` | 指针槽 `0x200daf70`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.stress.settings.ui_destroy` | 压力设置页面：UI 销毁回调 | `void1` | `health_stress_settings_ui_destroy` | 指针槽 `0x200daf88`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.settings.ui_create` | 睡眠设置页面：UI 创建回调 | `word3` | `health_sleep_settings_ui_create` | 指针槽 `0x200db350`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.settings.ui_destroy` | 睡眠设置页面：UI 销毁回调 | `void1` | `health_sleep_settings_ui_destroy` | 指针槽 `0x200db368`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.oxygen.settings.monitor_register` | 血氧设置：监测开关注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc64d586`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.settings.low_register` | 血氧设置：低血氧提醒入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc64d620`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.settings.click_data` | 血氧设置：读取点击入口类型 | `word1` | `lv_event_get_user_data` | 调用点 `0xc64d840`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.settings.low_initial_hide` | 血氧设置：初始化时隐藏低值提醒行 | `void2` | `lv_obj_add_flag` | 调用点 `0xc64d542`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.settings.low_initial_show` | 血氧设置：初始化时显示低值提醒行 | `void2` | `lv_obj_clear_flag` | 调用点 `0xc64d652`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.settings.low_disable_hide` | 血氧设置：关闭监测时隐藏低值提醒行 | `void2` | `lv_obj_add_flag` | 调用点 `0xc64d918`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.settings.low_refresh_hide` | 血氧设置：状态刷新时隐藏低值提醒行 | `void2` | `lv_obj_add_flag` | 调用点 `0xc64d6de`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.settings.low_refresh_show` | 血氧设置：状态刷新时显示低值提醒行 | `void2` | `lv_obj_clear_flag` | 调用点 `0xc64d72e`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.threshold.hint` | 血氧低值提醒：说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc64de00`、`0xc64db46`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.threshold.option_register_first` | 血氧低值提醒：首行回调注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc64de86`、`0xc64dbc8`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.threshold.option_register_default` | 血氧低值提醒：选项常规布局回调注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc64dec4`、`0xc64dc06`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.threshold.option_register_alt` | 血氧低值提醒：选项备用布局回调注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc64df58`、`0xc64dca6`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.threshold.option_count` | 血氧低值提醒：读取选项数量 | `word1` | `lv_event_get_user_data` | 调用点 `0xc64d9c4`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.threshold.option_target` | 血氧低值提醒：读取选项对象 | `word1` | `lv_event_current_target` | 调用点 `0xc64d9cc`，关闭对应页面后安装或卸载 | [oxygen-settings-actions-043.json](../evidence/oxygen-settings-actions-043.json) |
| `health.oxygen.settings.ui_create` | 血氧设置页面：UI 创建回调 | `word3` | `health_oxygen_settings_ui_create` | 指针槽 `0x200db608`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.oxygen.settings.ui_destroy` | 血氧设置页面：UI 销毁回调 | `void1` | `health_oxygen_settings_ui_destroy` | 指针槽 `0x200db620`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.breath.session.ui_create` | 呼吸过程页面：UI 创建回调 | `word3` | `health_breath_session_ui_create` | 指针槽 `0x200dacd4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.breath.session.ui_destroy` | 呼吸过程页面：UI 销毁回调 | `void1` | `health_breath_session_ui_destroy` | 指针槽 `0x200dacec`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.compass.calibration_icon` | 指南针：校准页面图标 | `void2` | `lv_image_set_src` | 调用点 `0xc4fdf32`，关闭指南针后安装或卸载 | [compass-view-043.json](../evidence/compass-view-043.json) |
| `apps.compass.calibration_hint` | 指南针：校准提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4fdf74`，关闭指南针后安装或卸载 | [compass-view-043.json](../evidence/compass-view-043.json) |
| `apps.compass.background` | 指南针：背景图 | `void2` | `lv_image_set_src` | 调用点 `0xc4fd88a`，关闭指南针后安装或卸载 | [compass-view-043.json](../evidence/compass-view-043.json) |
| `apps.compass.scale_normal` | 指南针：常规刻度图 | `void2` | `lv_image_set_src` | 调用点 `0xc4fdbba`，关闭指南针后安装或卸载 | [compass-view-043.json](../evidence/compass-view-043.json) |
| `apps.compass.scale_zero` | 指南针：零度刻度图 | `void2` | `lv_image_set_src` | 调用点 `0xc4fdbfe`，关闭指南针后安装或卸载 | [compass-view-043.json](../evidence/compass-view-043.json) |
| `apps.compass.north_icon` | 指南针：北方向标记图 | `void2` | `lv_image_set_src` | 调用点 `0xc4fdc28`，关闭指南针后安装或卸载 | [compass-view-043.json](../evidence/compass-view-043.json) |
| `apps.compass.east_icon` | 指南针：东方向标记图 | `void2` | `lv_image_set_src` | 调用点 `0xc4fdc64`，关闭指南针后安装或卸载 | [compass-view-043.json](../evidence/compass-view-043.json) |
| `apps.compass.south_icon` | 指南针：南方向标记图 | `void2` | `lv_image_set_src` | 调用点 `0xc4fdca2`，关闭指南针后安装或卸载 | [compass-view-043.json](../evidence/compass-view-043.json) |
| `apps.compass.west_icon` | 指南针：西方向标记图 | `void2` | `lv_image_set_src` | 调用点 `0xc4fdce0`，关闭指南针后安装或卸载 | [compass-view-043.json](../evidence/compass-view-043.json) |
| `apps.compass.degree_unit` | 指南针：角度单位 | `void2` | `lvx_label_set_text` | 调用点 `0xc4fdd4c`，关闭指南针后安装或卸载 | [compass-view-043.json](../evidence/compass-view-043.json) |
| `apps.compass.north_angle` | 指南针：北方向标记旋转角 | `void2` | `lv_image_set_angle` | 调用点 `0xc4fe000`；参数 1 为十分之一度，关闭指南针后安装或卸载 | [compass-rotation-043.json](../evidence/compass-rotation-043.json) |
| `apps.compass.east_angle` | 指南针：东方向标记旋转角 | `void2` | `lv_image_set_angle` | 调用点 `0xc4fe0ce`；参数 1 为十分之一度，关闭指南针后安装或卸载 | [compass-rotation-043.json](../evidence/compass-rotation-043.json) |
| `apps.compass.south_angle` | 指南针：南方向标记旋转角 | `void2` | `lv_image_set_angle` | 调用点 `0xc4fe0da`；参数 1 为十分之一度，关闭指南针后安装或卸载 | [compass-rotation-043.json](../evidence/compass-rotation-043.json) |
| `apps.compass.west_angle` | 指南针：西方向标记旋转角 | `void2` | `lv_image_set_angle` | 调用点 `0xc4fe0e6`；参数 1 为十分之一度，关闭指南针后安装或卸载 | [compass-rotation-043.json](../evidence/compass-rotation-043.json) |
| `apps.compass.ui_create` | 指南针主页面：UI 创建回调 | `word3` | `apps_compass_ui_create` | 指针槽 `0x200d0250`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.compass.ui_destroy` | 指南针主页面：UI 销毁回调 | `void1` | `apps_compass_ui_destroy` | 指针槽 `0x200d0268`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.flashlight.white_register` | 手电筒：白光页面事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc508952`，关闭手电筒页面后安装或卸载 | [flashlight-actions-043.json](../evidence/flashlight-actions-043.json) |
| `apps.flashlight.blink_register` | 手电筒：闪烁页面事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5086dc`，关闭手电筒页面后安装或卸载 | [flashlight-actions-043.json](../evidence/flashlight-actions-043.json) |
| `apps.flashlight.red_register` | 手电筒：红光页面事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5088b6`，关闭手电筒页面后安装或卸载 | [flashlight-actions-043.json](../evidence/flashlight-actions-043.json) |
| `apps.flashlight.page_register` | 手电筒：主视图事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc509062`，关闭手电筒页面后安装或卸载 | [flashlight-actions-043.json](../evidence/flashlight-actions-043.json) |
| `apps.flashlight.white_event_code` | 手电筒：白光事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc50898a`，关闭手电筒页面后安装或卸载 | [flashlight-actions-043.json](../evidence/flashlight-actions-043.json) |
| `apps.flashlight.blink_event_code` | 手电筒：闪烁事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc508a2e`，关闭手电筒页面后安装或卸载 | [flashlight-actions-043.json](../evidence/flashlight-actions-043.json) |
| `apps.flashlight.red_event_code` | 手电筒：红光事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc508ad2`，关闭手电筒页面后安装或卸载 | [flashlight-actions-043.json](../evidence/flashlight-actions-043.json) |
| `apps.flashlight.page_event_code` | 手电筒：主视图事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc5084ec`，关闭手电筒页面后安装或卸载 | [flashlight-actions-043.json](../evidence/flashlight-actions-043.json) |
| `apps.flashlight.warning_icon` | 手电筒：电量警告图标 | `void2` | `lv_image_set_src` | 调用点 `0xc508c14`，关闭手电筒页面后安装或卸载 | [flashlight-actions-043.json](../evidence/flashlight-actions-043.json) |
| `apps.flashlight.warning_title` | 手电筒：电量警告标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc508c4e`，关闭手电筒页面后安装或卸载 | [flashlight-actions-043.json](../evidence/flashlight-actions-043.json) |
| `apps.flashlight.warning_body` | 手电筒：电量警告正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc508c9e`，关闭手电筒页面后安装或卸载 | [flashlight-actions-043.json](../evidence/flashlight-actions-043.json) |
| `apps.flashlight.ui_create` | 手电筒主页面：UI 创建回调 | `word3` | `apps_flashlight_ui_create` | 指针槽 `0x200d07bc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.flashlight.ui_destroy` | 手电筒主页面：UI 销毁回调 | `void1` | `apps_flashlight_ui_destroy` | 指针槽 `0x200d07d4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.calendar.ui_create` | 日历主页面：UI 创建回调 | `word3` | `apps_calendar_ui_create` | 指针槽 `0x200cf668`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.calendar.ui_destroy` | 日历主页面：UI 销毁回调 | `void1` | `apps_calendar_ui_destroy` | 指针槽 `0x200cf680`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.stopwatch.start_register` | 秒表：开始按钮回调注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4fbb42`，关闭秒表后安装或卸载 | [stopwatch-actions-043.json](../evidence/stopwatch-actions-043.json) |
| `apps.stopwatch.pause_register` | 秒表：暂停按钮回调注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4fbb4e`，关闭秒表后安装或卸载 | [stopwatch-actions-043.json](../evidence/stopwatch-actions-043.json) |
| `apps.stopwatch.lap_register` | 秒表：计次按钮回调注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4fbb5a`，关闭秒表后安装或卸载 | [stopwatch-actions-043.json](../evidence/stopwatch-actions-043.json) |
| `apps.stopwatch.stop_register` | 秒表：停止并清零按钮回调注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4fbb66`，关闭秒表后安装或卸载 | [stopwatch-actions-043.json](../evidence/stopwatch-actions-043.json) |
| `apps.stopwatch.start_data` | 秒表：开始回调读取状态 | `word1` | `lv_event_get_user_data` | 调用点 `0xc4fa7d6`，关闭秒表后安装或卸载 | [stopwatch-actions-043.json](../evidence/stopwatch-actions-043.json) |
| `apps.stopwatch.pause_data` | 秒表：暂停回调读取状态 | `word1` | `lv_event_get_user_data` | 调用点 `0xc4fa6be`，关闭秒表后安装或卸载 | [stopwatch-actions-043.json](../evidence/stopwatch-actions-043.json) |
| `apps.stopwatch.lap_data` | 秒表：计次回调读取状态 | `word1` | `lv_event_get_user_data` | 调用点 `0xc4fb15c`，关闭秒表后安装或卸载 | [stopwatch-actions-043.json](../evidence/stopwatch-actions-043.json) |
| `apps.stopwatch.stop_data` | 秒表：停止回调读取状态 | `word1` | `lv_event_get_user_data` | 调用点 `0xc4fa940`，关闭秒表后安装或卸载 | [stopwatch-actions-043.json](../evidence/stopwatch-actions-043.json) |
| `apps.stopwatch.ui_create` | 秒表主页面：UI 创建回调 | `word3` | `apps_stopwatch_ui_create` | 指针槽 `0x200d0164`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.stopwatch.ui_destroy` | 秒表主页面：UI 销毁回调 | `void1` | `apps_stopwatch_ui_destroy` | 指针槽 `0x200d017c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `system.notifications.detail.ui_create` | 通知详情页面：UI 创建回调 | `word3` | `system_notifications_detail_ui_create` | 指针槽 `0x200d1180`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `system.notifications.detail.ui_destroy` | 通知详情页面：UI 销毁回调 | `void1` | `system_notifications_detail_ui_destroy` | 指针槽 `0x200d1198`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `system.notifications.aggregation.ui_create` | 通知聚合页面：UI 创建回调 | `word3` | `system_notifications_aggregation_ui_create` | 指针槽 `0x200d110c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `system.notifications.aggregation.ui_destroy` | 通知聚合页面：UI 销毁回调 | `void1` | `system_notifications_aggregation_ui_destroy` | 指针槽 `0x200d1124`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.activity.card_icon` | 活动详情：卡片图标 | `void2` | `lv_image_set_src` | 调用点 `0xc4d24f8`，页面状态槽 `0x2010dcd4`；安装前关闭活动页面 | [activity-cards-043.json](../evidence/activity-cards-043.json) |
| `health.activity.card_title` | 活动详情：卡片标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc4d257c`，页面状态槽 `0x2010dcd4`；安装前关闭活动页面 | [activity-cards-043.json](../evidence/activity-cards-043.json) |
| `health.activity.explain_register` | 活动详情：注册数据说明入口回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4d2746`，页面状态槽 `0x2010dcd4`；安装前关闭活动页面 | [activity-cards-043.json](../evidence/activity-cards-043.json) |
| `health.sedentary.complete_icon` | 久坐完成提醒：图标 | `void2` | `lv_image_set_src` | 调用点 `0xc4d3068`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.complete_title` | 久坐完成提醒：标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc4d309e`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.complete_tip` | 久坐完成提醒：说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc4d3100`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.message_icon` | 久坐通知：提醒图标 | `void2` | `lv_image_set_src` | 调用点 `0xc4d322e`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.message_title` | 久坐通知：活动标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc4d327c`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.message_prompt` | 久坐通知：活动提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc4d32c4`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.message_time` | 久坐通知：时间文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4d333c`、`0xc4d350e`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.primary_caption` | 久坐通知：首个按钮文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4d3402`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.no_reminder_caption` | 久坐通知：今日不再提醒按钮文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4d34aa`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.confirm_title` | 久坐通知：确认页面文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4d3746`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.primary_register` | 久坐通知：首个按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4d340e`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.no_reminder_register` | 久坐通知：今日不再提醒按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4d34b6`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.confirm_cancel_register` | 久坐通知确认页面：取消按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4d3788`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.sedentary.confirm_accept_register` | 久坐通知确认页面：确认按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4d37cc`，共用状态槽 `0x2010dd40`；安装前关闭久坐提醒及通知 | [sedentary-reminder-043.json](../evidence/sedentary-reminder-043.json) |
| `health.activity.ui_create` | 活动主页面：UI 创建回调 | `word3` | `health_activity_ui_create` | 指针槽 `0x200cf098`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.activity.ui_destroy` | 活动主页面：UI 销毁回调 | `void1` | `health_activity_ui_destroy` | 指针槽 `0x200cf0b0`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.media.ui_create` | 媒体主页面：UI 创建回调 | `word3` | `apps_media_ui_create` | 指针槽 `0x200d0f6c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.media.ui_destroy` | 媒体主页面：UI 销毁回调 | `void1` | `apps_media_ui_destroy` | 指针槽 `0x200d0f84`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.recorder.ui_create` | 录音主页面：UI 创建回调 | `word3` | `apps_recorder_ui_create` | 指针槽 `0x200da5d8`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.recorder.ui_destroy` | 录音主页面：UI 销毁回调 | `void1` | `apps_recorder_ui_destroy` | 指针槽 `0x200da5f0`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.vitality.ui_create` | 活力主页面：UI 创建回调 | `word3` | `health_vitality_ui_create` | 指针槽 `0x200db79c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.vitality.ui_destroy` | 活力主页面：UI 销毁回调 | `void1` | `health_vitality_ui_destroy` | 指针槽 `0x200db7b4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.women.ui_create` | 女性健康主页面：UI 创建回调 | `word3` | `health_women_ui_create` | 指针槽 `0x200da7ec`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.women.ui_destroy` | 女性健康主页面：UI 销毁回调 | `void1` | `health_women_ui_destroy` | 指针槽 `0x200da804`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.sound.ui_create` | 声音设置页面：UI 创建回调 | `word3` | `settings_sound_ui_create` | 指针槽 `0x200d3d68`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.sound.ui_destroy` | 声音设置页面：UI 销毁回调 | `void1` | `settings_sound_ui_destroy` | 指针槽 `0x200d3d80`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.vibration.ui_create` | 振动设置页面：UI 创建回调 | `word3` | `settings_vibration_ui_create` | 指针槽 `0x200d3ddc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.vibration.ui_destroy` | 振动设置页面：UI 销毁回调 | `void1` | `settings_vibration_ui_destroy` | 指针槽 `0x200d3df4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.notification_center.ui_create` | 通知中心设置页面：UI 创建回调 | `word3` | `settings_notification_center_ui_create` | 指针槽 `0x200d3898`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.notification_center.ui_destroy` | 通知中心设置页面：UI 销毁回调 | `void1` | `settings_notification_center_ui_destroy` | 指针槽 `0x200d38b0`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.control_center.ui_create` | 控制中心设置页面：UI 创建回调 | `word3` | `settings_control_center_ui_create` | 指针槽 `0x200d262c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.control_center.ui_destroy` | 控制中心设置页面：UI 销毁回调 | `void1` | `settings_control_center_ui_destroy` | 指针槽 `0x200d2644`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.activity.explain.section_title` | 活动数据说明：章节标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc4d1028`，四个章节共用；关闭说明页面后安装或卸载 | [activity-explain-043.json](../evidence/activity-explain-043.json) |
| `health.activity.explain.section_body` | 活动数据说明：章节正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc4d1066`，四个章节共用；关闭说明页面后安装或卸载 | [activity-explain-043.json](../evidence/activity-explain-043.json) |
| `health.activity.explain.ui_create` | 活动数据说明页面：UI 创建回调 | `word3` | `health_activity_explain_ui_create` | 指针槽 `0x200ceff4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.activity.explain.ui_destroy` | 活动数据说明页面：UI 销毁回调 | `void1` | `health_activity_explain_ui_destroy` | 指针槽 `0x200cf00c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.calendar.detail.title` | 日历详情：日程标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc4e692e`、`0xc4e6b26`，状态槽 `0x2010eb60`；关闭对应页面后安装或卸载 | [calendar-weather-details-043.json](../evidence/calendar-weather-details-043.json) |
| `apps.calendar.detail.location` | 日历详情：地点 | `void2` | `lvx_label_set_text` | 调用点 `0xc4e6a0a`，状态槽 `0x2010eb60`；关闭对应页面后安装或卸载 | [calendar-weather-details-043.json](../evidence/calendar-weather-details-043.json) |
| `apps.calendar.detail.description` | 日历详情：描述 | `void2` | `lvx_label_set_text` | 调用点 `0xc4e6ad6`，状态槽 `0x2010eb60`；关闭对应页面后安装或卸载 | [calendar-weather-details-043.json](../evidence/calendar-weather-details-043.json) |
| `apps.calendar.detail.location_icon` | 日历详情：地点图标 | `void2` | `lv_image_set_src` | 调用点 `0xc4e69ae`，状态槽 `0x2010eb60`；关闭对应页面后安装或卸载 | [calendar-weather-details-043.json](../evidence/calendar-weather-details-043.json) |
| `apps.calendar.detail.description_icon` | 日历详情：描述图标 | `void2` | `lv_image_set_src` | 调用点 `0xc4e6a70`，状态槽 `0x2010eb60`；关闭对应页面后安装或卸载 | [calendar-weather-details-043.json](../evidence/calendar-weather-details-043.json) |
| `apps.weather.forecast.day_icon` | 天气逐日预报：天气图标 | `void2` | `lv_image_set_src` | 调用点 `0xc60ee68`、`0xc60ef62`，状态槽 `0x2011ad70`；关闭对应页面后安装或卸载 | [calendar-weather-details-043.json](../evidence/calendar-weather-details-043.json) |
| `apps.weather.reminder.icon` | 天气连接提示：状态图标 | `void2` | `lv_image_set_src` | 调用点 `0xc60fd36`、`0xc60ff24`，状态槽 `0x2011ad88`；关闭对应页面后安装或卸载 | [calendar-weather-details-043.json](../evidence/calendar-weather-details-043.json) |
| `apps.weather.reminder.retry_text` | 天气连接提示：重试说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc60fdc6`，状态槽 `0x2011ad88`；关闭对应页面后安装或卸载 | [calendar-weather-details-043.json](../evidence/calendar-weather-details-043.json) |
| `apps.weather.reminder.disconnected_text` | 天气连接提示：连接断开说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc60fe8a`、`0xc60ff34`，状态槽 `0x2011ad88`；关闭对应页面后安装或卸载 | [calendar-weather-details-043.json](../evidence/calendar-weather-details-043.json) |
| `apps.weather.reminder.connected_text` | 天气连接提示：应用提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc60ff96`，状态槽 `0x2011ad88`；关闭对应页面后安装或卸载 | [calendar-weather-details-043.json](../evidence/calendar-weather-details-043.json) |
| `apps.weather.reminder.button_register` | 天气连接提示：确认按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc60fe5a`，状态槽 `0x2011ad88`；关闭对应页面后安装或卸载 | [calendar-weather-details-043.json](../evidence/calendar-weather-details-043.json) |
| `apps.calendar.detail.ui_create` | 日历日程详情页面：UI 创建回调 | `word3` | `apps_calendar_detail_ui_create` | 指针槽 `0x200cf5f4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.calendar.detail.ui_destroy` | 日历日程详情页面：UI 销毁回调 | `void1` | `apps_calendar_detail_ui_destroy` | 指针槽 `0x200cf60c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.weather.forecast.ui_create` | 天气逐日预报页面：UI 创建回调 | `word3` | `apps_weather_forecast_ui_create` | 指针槽 `0x200da3bc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.weather.forecast.ui_destroy` | 天气逐日预报页面：UI 销毁回调 | `void1` | `apps_weather_forecast_ui_destroy` | 指针槽 `0x200da3d4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.weather.reminder.ui_create` | 天气连接提示页面：UI 创建回调 | `word3` | `apps_weather_reminder_ui_create` | 指针槽 `0x200da4a4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.weather.reminder.ui_destroy` | 天气连接提示页面：UI 销毁回调 | `void1` | `apps_weather_reminder_ui_destroy` | 指针槽 `0x200da4bc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.weather.detail.draw_register` | 天气详情：根视图绘制事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc60ab18`，关闭天气详情页面后安装或卸载 | [weather-detail-actions-043.json](../evidence/weather-detail-actions-043.json) |
| `apps.weather.detail.draw_event_code` | 天气详情：绘制事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc60a096`，关闭天气详情页面后安装或卸载 | [weather-detail-actions-043.json](../evidence/weather-detail-actions-043.json) |
| `apps.weather.detail.refresh_register` | 天气详情：下拉刷新事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc60abc2`，关闭天气详情页面后安装或卸载 | [weather-detail-actions-043.json](../evidence/weather-detail-actions-043.json) |
| `apps.weather.detail.refresh_text` | 天气详情：下拉刷新中的文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc60a45c`，关闭天气详情页面后安装或卸载 | [weather-detail-actions-043.json](../evidence/weather-detail-actions-043.json) |
| `apps.weather.alert.row_register` | 天气预警列表：预警行点击事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc609706`，页面根槽 `0x200da23c`；关闭对应页面后安装或卸载 | [weather-alert-043.json](../evidence/weather-alert-043.json) |
| `apps.weather.alert.row_event_code` | 天气预警列表：行点击事件代码 | `word1` | `lv_event_get_code` | 调用点 `0xc609634`，页面根槽 `0x200da23c`；关闭对应页面后安装或卸载 | [weather-alert-043.json](../evidence/weather-alert-043.json) |
| `apps.weather.alert.row_icon` | 天气预警列表：预警图标 | `void2` | `lv_image_set_src` | 调用点 `0xc609716`，页面根槽 `0x200da23c`；关闭对应页面后安装或卸载 | [weather-alert-043.json](../evidence/weather-alert-043.json) |
| `apps.weather.alert.row_caption` | 天气预警列表：预警标签 | `void2` | `lvx_label_set_text` | 调用点 `0xc6097ee`，页面根槽 `0x200da23c`；关闭对应页面后安装或卸载 | [weather-alert-043.json](../evidence/weather-alert-043.json) |
| `apps.weather.alert.row_time` | 天气预警列表：时间文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc6098d2`，页面根槽 `0x200da23c`；关闭对应页面后安装或卸载 | [weather-alert-043.json](../evidence/weather-alert-043.json) |
| `apps.weather.alert_detail.caption` | 天气预警详情：预警标签 | `void2` | `lvx_label_set_text` | 调用点 `0xc609c1c`，页面根槽 `0x200da2b0`；关闭对应页面后安装或卸载 | [weather-alert-043.json](../evidence/weather-alert-043.json) |
| `apps.weather.alert_detail.body` | 天气预警详情：预警正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc609c5a`，页面根槽 `0x200da2b0`；关闭对应页面后安装或卸载 | [weather-alert-043.json](../evidence/weather-alert-043.json) |
| `apps.weather.detail.ui_create` | 天气详情页面：UI 创建回调 | `word3` | `apps_weather_detail_ui_create` | 指针槽 `0x200da340`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.weather.detail.ui_destroy` | 天气详情页面：UI 销毁回调 | `void1` | `apps_weather_detail_ui_destroy` | 指针槽 `0x200da358`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.oxygen.threshold.ui_create` | 血氧低值提醒设置页面：UI 创建回调 | `word3` | `health_oxygen_threshold_ui_create` | 指针槽 `0x200db67c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.oxygen.threshold.ui_destroy` | 血氧低值提醒设置页面：UI 销毁回调 | `void1` | `health_oxygen_threshold_ui_destroy` | 指针槽 `0x200db694`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.settings.switch_register` | 睡眠设置：开关回调注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc6410b4`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.settings.description` | 睡眠设置：选项说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc641110`、`0xc6411e0`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.settings_list.disturb_register` | 睡眠设置列表：睡眠模式入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc641964`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.settings_list.monitor_register` | 睡眠设置列表：高级监测入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc641972`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.settings_list.breath_register` | 睡眠设置列表：呼吸质量入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc641980`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.settings_list.hrv_register` | 睡眠设置列表：HRV 入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc641a30`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.settings_list.click_data` | 睡眠设置列表：读取设置类型 | `word1` | `lv_event_get_user_data` | 调用点 `0xc641746`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.survey.option_register` | 睡眠问卷：选项点击注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc640602`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.survey.option_target` | 睡眠问卷：读取选中对象 | `word1` | `lv_event_current_target` | 调用点 `0xc6407ea`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.survey.next_register` | 睡眠问卷：确认按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc640696`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.survey.question` | 睡眠问卷：问题文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc640582`、`0xc6408d4`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.survey_done.icon` | 睡眠问卷完成：图标 | `void2` | `lv_image_set_src` | 调用点 `0xc640c3c`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.survey_done.title` | 睡眠问卷完成：标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc640c9c`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.survey_done.description` | 睡眠问卷完成：说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc640cf8`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.survey_done.button_register` | 睡眠问卷完成：确认按钮 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc640d66`，关闭对应页面后安装或卸载 | [sleep-actions-043.json](../evidence/sleep-actions-043.json) |
| `health.sleep.settings_list.ui_create` | 睡眠设置列表页面：UI 创建回调 | `word3` | `health_sleep_settings_list_ui_create` | 指针槽 `0x200db3c4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.settings_list.ui_destroy` | 睡眠设置列表页面：UI 销毁回调 | `void1` | `health_sleep_settings_list_ui_destroy` | 指针槽 `0x200db3dc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.survey.ui_create` | 睡眠问卷页面：UI 创建回调 | `word3` | `health_sleep_survey_ui_create` | 指针槽 `0x200db238`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.survey.ui_destroy` | 睡眠问卷页面：UI 销毁回调 | `void1` | `health_sleep_survey_ui_destroy` | 指针槽 `0x200db250`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.survey_done.ui_create` | 睡眠问卷完成页面：UI 创建回调 | `word3` | `health_sleep_survey_done_ui_create` | 指针槽 `0x200db2dc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.survey_done.ui_destroy` | 睡眠问卷完成页面：UI 销毁回调 | `void1` | `health_sleep_survey_done_ui_destroy` | 指针槽 `0x200db2f4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.oxygen.measure.prep_icon` | 血氧测量：准备阶段图标 | `void2` | `lv_image_set_src` | 调用点 `0xc64c156`，关闭对应页面后安装或卸载 | [oxygen-measure-actions-043.json](../evidence/oxygen-measure-actions-043.json) |
| `health.oxygen.measure.prep_text` | 血氧测量：准备阶段提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc64c1ee`，关闭对应页面后安装或卸载 | [oxygen-measure-actions-043.json](../evidence/oxygen-measure-actions-043.json) |
| `health.oxygen.measure.still_text` | 血氧测量：保持静止提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc64c5dc`，关闭对应页面后安装或卸载 | [oxygen-measure-actions-043.json](../evidence/oxygen-measure-actions-043.json) |
| `health.oxygen.measure.motion_text` | 血氧测量：避免晃动提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc64c5fa`，关闭对应页面后安装或卸载 | [oxygen-measure-actions-043.json](../evidence/oxygen-measure-actions-043.json) |
| `health.oxygen.measure.skin_text` | 血氧测量：贴合皮肤提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc64c618`，关闭对应页面后安装或卸载 | [oxygen-measure-actions-043.json](../evidence/oxygen-measure-actions-043.json) |
| `health.oxygen.measure.screen_text` | 血氧测量：屏幕朝上提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc64c5be`，关闭对应页面后安装或卸载 | [oxygen-measure-actions-043.json](../evidence/oxygen-measure-actions-043.json) |
| `health.oxygen.measure.explain_data` | 血氧测量：读取说明入口数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc64c020`，关闭对应页面后安装或卸载 | [oxygen-measure-actions-043.json](../evidence/oxygen-measure-actions-043.json) |
| `health.oxygen.low_chart.info_icon` | 血氧低值图表：说明图标 | `void2` | `lv_image_set_src` | 调用点 `0xc64a248`、`0xc64a2bc`，关闭对应页面后安装或卸载 | [oxygen-measure-actions-043.json](../evidence/oxygen-measure-actions-043.json) |
| `health.oxygen.low_chart.info_register` | 血氧低值图表：说明入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc64a266`、`0xc64a2d8`，关闭对应页面后安装或卸载 | [oxygen-measure-actions-043.json](../evidence/oxygen-measure-actions-043.json) |
| `health.oxygen.measure.ui_create` | 血氧测量页面：UI 创建回调 | `word3` | `health_oxygen_measure_ui_create` | 指针槽 `0x200db594`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.oxygen.measure.ui_destroy` | 血氧测量页面：UI 销毁回调 | `void1` | `health_oxygen_measure_ui_destroy` | 指针槽 `0x200db5ac`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.oxygen.low_chart.ui_create` | 血氧低值图表页面：UI 创建回调 | `word3` | `health_oxygen_low_chart_ui_create` | 指针槽 `0x200db4ac`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.oxygen.low_chart.ui_destroy` | 血氧低值图表页面：UI 销毁回调 | `void1` | `health_oxygen_low_chart_ui_destroy` | 指针槽 `0x200db4c4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.breath.info.ui_create` | 呼吸练习说明页面：UI 创建回调 | `word3` | `health_breath_info_ui_create` | 指针槽 `0x200dabec`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.breath.info.ui_destroy` | 呼吸练习说明页面：UI 销毁回调 | `void1` | `health_breath_info_ui_destroy` | 指针槽 `0x200dac04`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.hrv_detail.average_text` | 平均 HRV 标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63cb8e`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_detail.low_text` | 低于正常文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc63cbea`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_detail.high_text` | 高于正常文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc63cc46`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_detail.no_data_text` | 无数据文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc63ccc0`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_detail.baseline_text` | 基线提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc63cd5e`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_detail.scale_text` | 个人范围文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc63cee8`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_detail.no_data_icon` | 无数据图标 | `void2` | `lv_image_set_src` | 调用点 `0xc63cdce`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_detail.info_icon` | 信息入口图标 | `void2` | `lv_image_set_src` | 调用点 `0xc63cfc0`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_detail.bar_icon` | 范围条图像 | `void2` | `lv_image_set_src` | 调用点 `0xc63cfea`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_detail.indicator_icon` | 范围指示图像 | `void2` | `lv_image_set_src` | 调用点 `0xc63d040`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_detail.info_register` | 信息入口事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc63cfcc`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_explain.title1` | HRV 说明第 1 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63d5d8`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_explain.detail1` | HRV 说明第 1 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63d5e6`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_explain.title2` | HRV 说明第 2 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63d5f4`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_explain.detail2` | HRV 说明第 2 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63d602`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_explain.title3` | HRV 说明第 3 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63d610`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_explain.detail3` | HRV 说明第 3 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63d61e`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_explain.title4` | HRV 说明第 4 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63d62c`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_explain.detail4` | HRV 说明第 4 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63d63a`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.normal_title1` | HRV 信息 normal 分支第 1 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dc38`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.normal_detail1` | HRV 信息 normal 分支第 1 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dc46`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.normal_title2` | HRV 信息 normal 分支第 2 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dc54`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.normal_detail2` | HRV 信息 normal 分支第 2 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dc62`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.normal_title3` | HRV 信息 normal 分支第 3 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dc70`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.normal_detail3` | HRV 信息 normal 分支第 3 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dc7e`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.high_title1` | HRV 信息 high 分支第 1 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63db5e`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.high_detail1` | HRV 信息 high 分支第 1 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63db6c`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.high_title2` | HRV 信息 high 分支第 2 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63db7a`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.high_detail2` | HRV 信息 high 分支第 2 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63db88`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.high_title3` | HRV 信息 high 分支第 3 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63db96`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.high_detail3` | HRV 信息 high 分支第 3 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dba4`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.high_title4` | HRV 信息 high 分支第 4 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dbb2`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.high_detail4` | HRV 信息 high 分支第 4 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dbc0`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.low_title1` | HRV 信息 low 分支第 1 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dcb8`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.low_detail1` | HRV 信息 low 分支第 1 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dcc6`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.low_title2` | HRV 信息 low 分支第 2 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dcd4`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.low_detail2` | HRV 信息 low 分支第 2 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dce2`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.low_title3` | HRV 信息 low 分支第 3 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dcf0`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.low_detail3` | HRV 信息 low 分支第 3 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dcfe`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.low_title4` | HRV 信息 low 分支第 4 段标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dd0c`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_info.low_detail4` | HRV 信息 low 分支第 4 段正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc63dd1a`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.stress.measure.prep_icon` | 测量准备图标 | `void2` | `lv_image_set_src` | 调用点 `0xc631bea`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.stress.measure.prep_text` | 测量准备文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc631c82`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.stress.measure.measuring_text` | 测量中状态文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc632504`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.stress.measure.screen_up_text` | 屏幕朝上提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc6325ae`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.stress.measure.still_text` | 保持静止提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc632628`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.stress.month.date_today` | 图表日期标签一 | `void2` | `lvx_label_set_text` | 调用点 `0xc632ee0`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.stress.month.date_prev1` | 图表日期标签二 | `void2` | `lvx_label_set_text` | 调用点 `0xc632f36`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.stress.month.date_prev2` | 图表日期标签三 | `void2` | `lvx_label_set_text` | 调用点 `0xc632f88`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.stress.month.empty_value` | 无数据数值占位 | `void2` | `lvx_label_set_text` | 调用点 `0xc6331f6`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.stress.month.average_label` | 平均值说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc633244`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.stress.month.chart_register` | 图表事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc63302c`，关闭对应页面后安装或卸载 | [hrv-stress-actions-043.json](../evidence/hrv-stress-actions-043.json) |
| `health.sleep.hrv_detail.ui_create` | 睡眠心率变异性详情页面：UI 创建回调 | `word3` | `health_sleep_hrv_detail_ui_create` | 指针槽 `0x200db058`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.hrv_detail.ui_destroy` | 睡眠心率变异性详情页面：UI 销毁回调 | `void1` | `health_sleep_hrv_detail_ui_destroy` | 指针槽 `0x200db070`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.hrv_explain.ui_create` | 睡眠心率变异性说明页面：UI 创建回调 | `word3` | `health_sleep_hrv_explain_ui_create` | 指针槽 `0x200db0cc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.hrv_explain.ui_destroy` | 睡眠心率变异性说明页面：UI 销毁回调 | `void1` | `health_sleep_hrv_explain_ui_destroy` | 指针槽 `0x200db0e4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.hrv_info.ui_create` | 睡眠心率变异性信息页面：UI 创建回调 | `word3` | `health_sleep_hrv_info_ui_create` | 指针槽 `0x200db140`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.hrv_info.ui_destroy` | 睡眠心率变异性信息页面：UI 销毁回调 | `void1` | `health_sleep_hrv_info_ui_destroy` | 指针槽 `0x200db158`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.stress.measure.ui_create` | 压力测量页面：UI 创建回调 | `word3` | `health_stress_measure_ui_create` | 指针槽 `0x200dae88`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.stress.measure.ui_destroy` | 压力测量页面：UI 销毁回调 | `void1` | `health_stress_measure_ui_destroy` | 指针槽 `0x200daea0`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.stress.month.ui_create` | 压力月度页面：UI 创建回调 | `word3` | `health_stress_month_ui_create` | 指针槽 `0x200daefc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.stress.month.ui_destroy` | 压力月度页面：UI 销毁回调 | `void1` | `health_stress_month_ui_destroy` | 指针槽 `0x200daf14`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.stress.explain.text1` | 压力说明文字 saturation1 | `void2` | `lvx_label_set_text` | 调用点 `0xc62db5c`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.stress.explain.text2` | 压力说明文字 saturation2 | `void2` | `lvx_label_set_text` | 调用点 `0xc62dba2`、`0xc62df82`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.stress.explain.text3` | 压力说明文字 saturation3 | `void2` | `lvx_label_set_text` | 调用点 `0xc62dbee`、`0xc62dfce`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.stress.explain.text4` | 压力说明文字 saturation4 | `void2` | `lvx_label_set_text` | 调用点 `0xc62dd0a`、`0xc62e0ea`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.stress.explain.text5` | 压力说明文字 saturation5 | `void2` | `lvx_label_set_text` | 调用点 `0xc62dd50`、`0xc62e130`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.stress.explain.text8` | 压力说明文字 saturation8 | `void2` | `lvx_label_set_text` | 调用点 `0xc62de80`、`0xc62e260`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.stress.explain.text9` | 压力说明文字 saturation9 | `void2` | `lvx_label_set_text` | 调用点 `0xc62dcbe`、`0xc62e09e`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.stress.explain.wear_icon1` | 压力说明佩戴图像 1 | `void2` | `lv_image_set_src` | 调用点 `0xc62ddd2`、`0xc62e1b2`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.stress.explain.wear_icon2` | 压力说明佩戴图像 2 | `void2` | `lv_image_set_src` | 调用点 `0xc62de3e`、`0xc62e21e`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.explain.wear_text1` | 心率测量说明文字 1 | `void2` | `lvx_label_set_text` | 调用点 `0xc664664`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.explain.wear_text2` | 心率测量说明文字 2 | `void2` | `lvx_label_set_text` | 调用点 `0xc6646e2`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.explain.wear_text5` | 心率测量说明文字 5 | `void2` | `lvx_label_set_text` | 调用点 `0xc66473c`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.explain.wear_text6` | 心率测量说明文字 6 | `void2` | `lvx_label_set_text` | 调用点 `0xc664796`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.explain.wear_icon1` | 心率测量说明佩戴图像 1 | `void2` | `lv_image_set_src` | 调用点 `0xc664602`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.explain.wear_icon2` | 心率测量说明佩戴图像 2 | `void2` | `lv_image_set_src` | 调用点 `0xc664688`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.explain.detail_text` | 心率说明页多段文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc664534`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.abnormal.beat_text` | 异常心率：心搏说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc663878`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.abnormal.info_icon` | 异常心率：说明图标 | `void2` | `lv_image_set_src` | 调用点 `0xc663412`、`0xc6638b8`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.abnormal.info_register` | 异常心率：说明入口事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc663422`、`0xc6638c8`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.abnormal.chart_register` | 异常心率：图表绘制事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc662f06`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.abnormal.chart_div` | 异常心率：图表分隔线图像 | `void2` | `lv_image_set_src` | 调用点 `0xc66307a`、`0xc66309e`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.rest.date_today` | 图表日期标签一 | `void2` | `lvx_label_set_text` | 调用点 `0xc667bb2`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.rest.date_prev1` | 图表日期标签二 | `void2` | `lvx_label_set_text` | 调用点 `0xc667c1e`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.rest.date_prev2` | 图表日期标签三 | `void2` | `lvx_label_set_text` | 调用点 `0xc667cac`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.heart_rate.rest.chart_register` | 静息心率：图表绘制事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc667d02`，关闭对应页面后安装或卸载 | [heart-stress-more-043.json](../evidence/heart-stress-more-043.json) |
| `health.stress.explain.ui_create` | 压力说明页面：UI 创建回调 | `word3` | `health_stress_explain_ui_create` | 指针槽 `0x200dada0`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.stress.explain.ui_destroy` | 压力说明页面：UI 销毁回调 | `void1` | `health_stress_explain_ui_destroy` | 指针槽 `0x200dadb8`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.heart_rate.abnormal.ui_create` | 异常心率页面：UI 创建回调 | `word3` | `health_heart_rate_abnormal_ui_create` | 指针槽 `0x200dbde4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.heart_rate.abnormal.ui_destroy` | 异常心率页面：UI 销毁回调 | `void1` | `health_heart_rate_abnormal_ui_destroy` | 指针槽 `0x200dbdfc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.heart_rate.explain.ui_create` | 心率说明页面：UI 创建回调 | `word3` | `health_heart_rate_explain_ui_create` | 指针槽 `0x200dbe58`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.heart_rate.explain.ui_destroy` | 心率说明页面：UI 销毁回调 | `void1` | `health_heart_rate_explain_ui_destroy` | 指针槽 `0x200dbe70`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.heart_rate.rest.ui_create` | 静息心率页面：UI 创建回调 | `word3` | `health_heart_rate_rest_ui_create` | 指针槽 `0x200dbfc8`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.heart_rate.rest.ui_destroy` | 静息心率页面：UI 销毁回调 | `void1` | `health_heart_rate_rest_ui_destroy` | 指针槽 `0x200dbfe0`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.heart_rate.catalog.ui_create` | 心率设置目录页面：UI 创建回调 | `void3` | `health_heart_rate_catalog_ui_create` | 指针槽 `0x200dc124`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.heart_rate.catalog.ui_destroy` | 心率设置目录页面：UI 销毁回调 | `void1` | `health_heart_rate_catalog_ui_destroy` | 指针槽 `0x200dc13c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.list_edit.flag_icon` | 列表编辑：标记图标 | `void2` | `lv_image_set_src` | 调用点 `0xc58f414`，关闭对应页面后安装或卸载 | [sports-pages-assets-043.json](../evidence/sports-pages-assets-043.json) |
| `sports.list_edit.delete_icon` | 列表编辑：删除图标 | `void2` | `lv_image_set_src` | 调用点 `0xc58f42a`，关闭对应页面后安装或卸载 | [sports-pages-assets-043.json](../evidence/sports-pages-assets-043.json) |
| `sports.list_edit.gradient_icon` | 列表编辑：底部渐变图 | `void2` | `lv_image_set_src` | 调用点 `0xc58f506`，关闭对应页面后安装或卸载 | [sports-pages-assets-043.json](../evidence/sports-pages-assets-043.json) |
| `sports.countdown.initial_icon` | 运动倒计时：初始图像 | `void2` | `lv_image_set_src` | 调用点 `0xc596d7a`，关闭对应页面后安装或卸载 | [sports-pages-assets-043.json](../evidence/sports-pages-assets-043.json) |
| `sports.countdown.animation_icon` | 运动倒计时：动画帧图像 | `void2` | `lv_image_set_src` | 调用点 `0xc596e60`，关闭对应页面后安装或卸载 | [sports-pages-assets-043.json](../evidence/sports-pages-assets-043.json) |
| `sports.categories.ui_create` | 运动分类页面：UI 创建回调 | `word3` | `sports_categories_ui_create` | 指针槽 `0x200d4f7c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.categories.ui_destroy` | 运动分类页面：UI 销毁回调 | `void1` | `sports_categories_ui_destroy` | 指针槽 `0x200d4f94`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.category_list.ui_create` | 同一运动分类列表页面：UI 创建回调 | `word3` | `sports_category_list_ui_create` | 指针槽 `0x200d50e4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.category_list.ui_destroy` | 同一运动分类列表页面：UI 销毁回调 | `void1` | `sports_category_list_ui_destroy` | 指针槽 `0x200d50fc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.list_edit.ui_create` | 运动列表编辑页面：UI 创建回调 | `word3` | `sports_list_edit_ui_create` | 指针槽 `0x200d4ff0`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.list_edit.ui_destroy` | 运动列表编辑页面：UI 销毁回调 | `void1` | `sports_list_edit_ui_destroy` | 指针槽 `0x200d5008`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.countdown.ui_create` | 运动倒计时页面：UI 创建回调 | `word3` | `sports_countdown_ui_create` | 指针槽 `0x200d53cc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.countdown.ui_destroy` | 运动倒计时页面：UI 销毁回调 | `void1` | `sports_countdown_ui_destroy` | 指针槽 `0x200d53e4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.switch.register` | 提醒开关：行事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5bf0a0`、`0xc5bf0c6`，关闭对应页面后安装或卸载 | [sports-settings-actions-043.json](../evidence/sports-settings-actions-043.json) |
| `sports.settings.switch.event_data` | 提醒开关：事件参数读取 | `word1` | `lv_event_get_user_data` | 调用点 `0xc5bf01e`，关闭对应页面后安装或卸载 | [sports-settings-actions-043.json](../evidence/sports-settings-actions-043.json) |
| `sports.settings.picker.confirm_register` | 数值选择：确认注册（一） | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5bd660`、`0xc5bd7a2`，关闭对应页面后安装或卸载 | [sports-settings-actions-043.json](../evidence/sports-settings-actions-043.json) |
| `sports.settings.picker.confirm_register_alt` | 数值选择：确认注册（二） | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5bd8c0`、`0xc5bdc46`，关闭对应页面后安装或卸载 | [sports-settings-actions-043.json](../evidence/sports-settings-actions-043.json) |
| `sports.settings.picker.event_data` | 数值选择：确认事件参数读取 | `word1` | `lv_event_get_user_data` | 调用点 `0xc5bca10`，关闭对应页面后安装或卸载 | [sports-settings-actions-043.json](../evidence/sports-settings-actions-043.json) |
| `sports.settings.picker.change_register` | 数值选择：滚轮事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5bda56`，关闭对应页面后安装或卸载 | [sports-settings-actions-043.json](../evidence/sports-settings-actions-043.json) |
| `sports.settings.picker.focus_register` | 数值选择：滚轮焦点注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5bda62`，关闭对应页面后安装或卸载 | [sports-settings-actions-043.json](../evidence/sports-settings-actions-043.json) |
| `sports.settings.picker.value_register` | 数值选择：滚轮变化注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5bda6e`，关闭对应页面后安装或卸载 | [sports-settings-actions-043.json](../evidence/sports-settings-actions-043.json) |
| `sports.settings.radio.runway_register` | 单选页：跑道确认注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5c25aa`，关闭对应页面后安装或卸载 | [sports-settings-actions-043.json](../evidence/sports-settings-actions-043.json) |
| `sports.settings.radio.runway_data` | 单选页：跑道确认事件参数 | `word1` | `lv_event_get_user_data` | 调用点 `0xc5c198a`，关闭对应页面后安装或卸载 | [sports-settings-actions-043.json](../evidence/sports-settings-actions-043.json) |
| `sports.settings.radio.gradient` | 单选页：底部渐变图 | `void2` | `lv_image_set_src` | 调用点 `0xc5c24fe`，关闭对应页面后安装或卸载 | [sports-settings-actions-043.json](../evidence/sports-settings-actions-043.json) |
| `sports.settings.radio.mask` | 单选页：渐变遮罩图 | `void2` | `lv_image_set_src` | 调用点 `0xc5c250e`，关闭对应页面后安装或卸载 | [sports-settings-actions-043.json](../evidence/sports-settings-actions-043.json) |
| `sports.settings.ui_create` | 运动设置主页面：UI 创建回调 | `word3` | `sports_settings_ui_create` | 指针槽 `0x200d7f98`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.ui_destroy` | 运动设置主页面：UI 销毁回调 | `void1` | `sports_settings_ui_destroy` | 指针槽 `0x200d7fb0`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.detail.ui_create` | 运动设置详情页面：UI 创建回调 | `word3` | `sports_settings_detail_ui_create` | 指针槽 `0x200d7ccc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.detail.ui_destroy` | 运动设置详情页面：UI 销毁回调 | `void1` | `sports_settings_detail_ui_destroy` | 指针槽 `0x200d7ce4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.switch.ui_create` | 运动提醒开关页面：UI 创建回调 | `word3` | `sports_settings_switch_ui_create` | 指针槽 `0x200d8058`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.switch.ui_destroy` | 运动提醒开关页面：UI 销毁回调 | `void1` | `sports_settings_switch_ui_destroy` | 指针槽 `0x200d8070`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.radio.ui_create` | 运动设置单选页面：UI 创建回调 | `word3` | `sports_settings_radio_ui_create` | 指针槽 `0x200d7f24`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.radio.ui_destroy` | 运动设置单选页面：UI 销毁回调 | `void1` | `sports_settings_radio_ui_destroy` | 指针槽 `0x200d7f3c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.picker.ui_create` | 运动设置数值选择页面：UI 创建回调 | `word3` | `sports_settings_picker_ui_create` | 指针槽 `0x200d7eb0`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.picker.ui_destroy` | 运动设置数值选择页面：UI 销毁回调 | `void1` | `sports_settings_picker_ui_destroy` | 指针槽 `0x200d7ec8`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.waiting.start_register` | 运动准备：启动入口事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5cdae6`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.start_data` | 运动准备：启动事件参数读取 | `word1` | `lv_event_get_user_data` | 调用点 `0xc5cd7a2`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.settings_register` | 运动准备：设置入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5cdb64`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.settings_data` | 运动准备：设置事件参数读取 | `word1` | `lv_event_get_user_data` | 调用点 `0xc5cce44`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.warmup_register` | 运动准备：热身入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5cdc80`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.warmup_data` | 运动准备：热身事件参数读取 | `word1` | `lv_event_get_user_data` | 调用点 `0xc5ccfa6`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.swim_register` | 运动准备：泳池长度入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5cddfc`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.swim_data` | 运动准备：泳池事件参数读取 | `word1` | `lv_event_get_user_data` | 调用点 `0xc5cce7e`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.runway_register` | 运动准备：跑道设置入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5cdcea`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.course_info_register` | 运动准备：课程说明入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5ccbd8`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.course_info_icon` | 运动准备：课程说明图标 | `void2` | `lv_image_set_src` | 调用点 `0xc5ccbc4`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.sport_text` | 运动准备：运动名称文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5cdb20`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.course_text` | 运动准备：课程名称文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5cdbd2`，关闭对应页面后安装或卸载 | [sports-waiting-actions-043.json](../evidence/sports-waiting-actions-043.json) |
| `sports.waiting.ui_create` | 运动准备页面：UI 创建回调 | `word3` | `sports_waiting_ui_create` | 指针槽 `0x200d851c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.waiting.ui_destroy` | 运动准备页面：UI 销毁回调 | `void1` | `sports_waiting_ui_destroy` | 指针槽 `0x200d8534`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.realtime.ui_create` | 运动实时页面：UI 创建回调 | `word3` | `sports_realtime_ui_create` | 指针槽 `0x200d5354`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.realtime.ui_destroy` | 运动实时页面：UI 销毁回调 | `void1` | `sports_realtime_ui_destroy` | 指针槽 `0x200d536c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.voice.ui_create` | 运动语音音量页面：UI 创建回调 | `word3` | `sports_voice_ui_create` | 指针槽 `0x200d559c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.voice.ui_destroy` | 运动语音音量页面：UI 销毁回调 | `void1` | `sports_voice_ui_destroy` | 指针槽 `0x200d55b4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.warmup.start_register` | 热身页：开始注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5d170e`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup.switch_register` | 热身页：切换入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5d1926`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup.explain_register` | 热身页：说明入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5d19e4`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup.switch_icon` | 热身页：切换图标 | `void2` | `lv_image_set_src` | 调用点 `0xc5d186e`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup.run_text` | 热身页：跑前热身文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5d1750`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup.long_run_text` | 热身页：长跑热身文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5d1a6a`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup.cycling_text` | 热身页：骑行热身文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5d1b50`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup.whole_body_text` | 热身页：全身热身文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5d1bc2`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup.rope_text` | 热身页：跳绳热身文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5d1c14`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup_anim.pause_register` | 热身动画：暂停入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5cf26c`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup_anim.resume_register` | 热身动画：继续入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5cf2ac`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup_anim.end_register` | 热身动画：结束入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5cf2f0`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup_anim.end_event_code` | 热身动画：结束事件类型读取 | `word1` | `lv_event_get_code` | 调用点 `0xc5d0530`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup_anim.paused_text` | 热身动画：暂停状态文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5d1046`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup_anim.preview_text` | 热身动画：动作预览文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5d0fb0`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup_explain.action_text` | 热身说明：动作名称 | `void2` | `lvx_label_set_text` | 调用点 `0xc5ce76e`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup_explain.duration_text` | 热身说明：动作时间或次数 | `void2` | `lvx_label_set_text` | 调用点 `0xc5ce61c`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.settings.ephemeris.valid_text` | 星历页：有效期说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc5b9e94`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.settings.ephemeris.expired_text` | 星历页：过期提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc5ba0ee`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.settings.ephemeris.status_text` | 星历页：更新影响说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc5ba168`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.settings.ephemeris.info_icon` | 星历页：说明图标 | `void2` | `lv_image_set_src` | 调用点 `0xc5ba188`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.settings.ephemeris.info_register` | 星历页：说明入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5ba19c`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.settings.ephemeris.update_register` | 星历页：更新入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5ba20c`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.settings.ephemeris_sub.position_text` | 星历子页：定位说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc5ba9c8`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.settings.ephemeris_sub.progress_text` | 星历子页：更新进度说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc5baae4`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.settings.ephemeris_sub.network_text` | 星历子页：网络说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc5bac02`，关闭对应页面后安装或卸载 | [sports-warmup-actions-043.json](../evidence/sports-warmup-actions-043.json) |
| `sports.warmup.ui_create` | 运动热身页面：UI 创建回调 | `word3` | `sports_warmup_ui_create` | 指针槽 `0x200d8700`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.warmup.ui_destroy` | 运动热身页面：UI 销毁回调 | `void1` | `sports_warmup_ui_destroy` | 指针槽 `0x200d8718`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.warmup_explain.ui_create` | 运动热身说明页面：UI 创建回调 | `word3` | `sports_warmup_explain_ui_create` | 指针槽 `0x200d860c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.warmup_explain.ui_destroy` | 运动热身说明页面：UI 销毁回调 | `void1` | `sports_warmup_explain_ui_destroy` | 指针槽 `0x200d8624`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.warmup_anim.ui_create` | 运动热身动画页面：UI 创建回调 | `word3` | `sports_warmup_anim_ui_create` | 指针槽 `0x200d8680`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.warmup_anim.ui_destroy` | 运动热身动画页面：UI 销毁回调 | `void1` | `sports_warmup_anim_ui_destroy` | 指针槽 `0x200d8698`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.ephemeris.ui_create` | 运动星历更新页面：UI 创建回调 | `word3` | `sports_settings_ephemeris_ui_create` | 指针槽 `0x200d7d40`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.ephemeris.ui_destroy` | 运动星历更新页面：UI 销毁回调 | `void1` | `sports_settings_ephemeris_ui_destroy` | 指针槽 `0x200d7d58`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.ephemeris_sub.ui_create` | 运动星历更新子页面：UI 创建回调 | `word3` | `sports_settings_ephemeris_sub_ui_create` | 指针槽 `0x200d7db4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.ephemeris_sub.ui_destroy` | 运动星历更新子页面：UI 销毁回调 | `void1` | `sports_settings_ephemeris_sub_ui_destroy` | 指针槽 `0x200d7dcc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.general.ui_create` | 运动通用设置页面：UI 创建回调 | `word3` | `sports_settings_general_ui_create` | 指针槽 `0x200d7e28`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `sports.settings.general.ui_destroy` | 运动通用设置页面：UI 销毁回调 | `void1` | `sports_settings_general_ui_destroy` | 指针槽 `0x200d7e40`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.pomodoro.main.set_text` | 主页面：设置时间文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5457b4`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.main.set_register` | 主页面：设置时间入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5457d8`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.main.start_icon` | 主页面：可点击图标 | `void2` | `lv_image_set_src` | 调用点 `0xc5457fe`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.main.start_register` | 主页面：开始入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc545850`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.activity.set_text` | 进行页面：设置时间文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5444d6`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.activity.click_icon` | 进行页面：可点击图标 | `void2` | `lv_image_set_src` | 调用点 `0xc544514`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.activity.end_register` | 进行页面：结束入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5445b4`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.activity.control_register` | 进行页面：运行控制入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5445fa`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.activity.state_text` | 进行页面：专注或休息文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc544ca2`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.end.confirm_register` | 结束页面：确认入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc54518c`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.notice.icon` | 提示页面：图标 | `void2` | `lv_image_set_src` | 调用点 `0xc545f46`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.notice.text` | 提示页面：提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc545fa2`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.notice.confirm_register` | 提示页面：确认入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc545fdc`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.info.name_text` | 说明页面：名称文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5453ec`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.set.roller_register` | 设置页面：滚轮事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5462d4`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.set.confirm_register` | 设置页面：确认入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5463b8`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.set.unit_text` | 设置页面：分钟单位文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc546352`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.set.top_shadow` | 设置页面：上方渐变图 | `void2` | `lv_image_set_src` | 调用点 `0xc5462f8`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.set.bottom_shadow` | 设置页面：下方渐变图 | `void2` | `lv_image_set_src` | 调用点 `0xc54631e`，关闭对应页面后安装或卸载 | [pomodoro-actions-043.json](../evidence/pomodoro-actions-043.json) |
| `apps.pomodoro.main.ui_create` | 番茄专注主页面：UI 创建回调 | `word3` | `apps_pomodoro_main_ui_create` | 指针槽 `0x200d1bd4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.pomodoro.main.ui_destroy` | 番茄专注主页面：UI 销毁回调 | `void1` | `apps_pomodoro_main_ui_destroy` | 指针槽 `0x200d1bec`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.pomodoro.set.ui_create` | 番茄专注时长设置页面：UI 创建回调 | `word3` | `apps_pomodoro_set_ui_create` | 指针槽 `0x200d1cbc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.pomodoro.set.ui_destroy` | 番茄专注时长设置页面：UI 销毁回调 | `void1` | `apps_pomodoro_set_ui_destroy` | 指针槽 `0x200d1cd4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.pomodoro.info.ui_create` | 番茄专注说明页面：UI 创建回调 | `word3` | `apps_pomodoro_info_ui_create` | 指针槽 `0x200d1b60`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.pomodoro.info.ui_destroy` | 番茄专注说明页面：UI 销毁回调 | `void1` | `apps_pomodoro_info_ui_destroy` | 指针槽 `0x200d1b78`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.pomodoro.activity.ui_create` | 番茄专注进行页面：UI 创建回调 | `word3` | `apps_pomodoro_activity_ui_create` | 指针槽 `0x200d1a58`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.pomodoro.activity.ui_destroy` | 番茄专注进行页面：UI 销毁回调 | `void1` | `apps_pomodoro_activity_ui_destroy` | 指针槽 `0x200d1a70`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.pomodoro.notice.ui_create` | 番茄专注提示页面：UI 创建回调 | `word3` | `apps_pomodoro_notice_ui_create` | 指针槽 `0x200d1c48`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.pomodoro.notice.ui_destroy` | 番茄专注提示页面：UI 销毁回调 | `void1` | `apps_pomodoro_notice_ui_destroy` | 指针槽 `0x200d1c60`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.pomodoro.end.ui_create` | 番茄专注结束页面：UI 创建回调 | `word3` | `apps_pomodoro_end_ui_create` | 指针槽 `0x200d1aec`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.pomodoro.end.ui_destroy` | 番茄专注结束页面：UI 销毁回调 | `void1` | `apps_pomodoro_end_ui_destroy` | 指针槽 `0x200d1b04`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.alarm.custom.confirm_register` | 自定义重复页：确认入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc53c2b6`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.edit.confirm_register` | 编辑页：保存入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc53d256`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.edit.confirm_data` | 编辑页：保存事件参数 | `word1` | `lv_event_get_user_data` | 调用点 `0xc53c720`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.edit.row_register` | 编辑页：动态设置行事件 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc53ca84`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.edit.switch_register` | 编辑页：智能提醒开关事件 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc53cc32`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.edit.off_text` | 编辑页：智能提醒关闭文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc53cc20`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.edit.on_text` | 编辑页：智能提醒开启文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc53cd4c`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.edit.remind_text` | 编辑页：提醒文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc53cc74`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.smart.options_register` | 智能提醒页：两个选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc53f35c`、`0xc53f398`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.smart.event_code` | 智能提醒页：事件类型读取 | `word1` | `lv_event_get_code` | 调用点 `0xc53f45c`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.smart.choice` | 智能提醒页：选项数据读取 | `word1` | `lv_event_get_user_data` | 调用点 `0xc53f46c`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.smart.title_text` | 智能提醒页：标题文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc53f2b6`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.smart.info_text` | 智能提醒页：说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc53f302`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.time.roller_register` | 时间页：时分滚轮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc53fb2a`、`0xc53fbaa`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.time.ampm_register` | 时间页：上午下午滚轮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc53fe4c`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.time.roller_event_code` | 时间页：滚轮事件类型读取 | `word1` | `lv_event_get_code` | 调用点 `0xc53f5cc`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.time.confirm_register` | 时间页：确认入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc53fd44`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.time.confirm_data` | 时间页：确认事件参数 | `word1` | `lv_event_get_user_data` | 调用点 `0xc53f758`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.time.hour_text` | 时间页：小时提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc53f6b0`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.time.minute_text` | 时间页：分钟提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc53f6fe`，关闭对应页面后安装或卸载 | [alarm-pages-actions-043.json](../evidence/alarm-pages-actions-043.json) |
| `apps.alarm.custom.ui_create` | 闹钟自定义重复页面：UI 创建回调 | `word3` | `apps_alarm_custom_ui_create` | 指针槽 `0x200d13ac`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.alarm.custom.ui_destroy` | 闹钟自定义重复页面：UI 销毁回调 | `void1` | `apps_alarm_custom_ui_destroy` | 指针槽 `0x200d13c4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.alarm.edit.ui_create` | 闹钟编辑页面：UI 创建回调 | `word3` | `apps_alarm_edit_ui_create` | 指针槽 `0x200d1448`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.alarm.edit.ui_destroy` | 闹钟编辑页面：UI 销毁回调 | `void1` | `apps_alarm_edit_ui_destroy` | 指针槽 `0x200d1460`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.alarm.repeat_page.ui_create` | 闹钟重复规则页面：UI 创建回调 | `word3` | `apps_alarm_repeat_page_ui_create` | 指针槽 `0x200d1580`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.alarm.repeat_page.ui_destroy` | 闹钟重复规则页面：UI 销毁回调 | `void1` | `apps_alarm_repeat_page_ui_destroy` | 指针槽 `0x200d1598`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.alarm.smart.ui_create` | 闹钟智能提醒页面：UI 创建回调 | `word3` | `apps_alarm_smart_ui_create` | 指针槽 `0x200d161c`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.alarm.smart.ui_destroy` | 闹钟智能提醒页面：UI 销毁回调 | `void1` | `apps_alarm_smart_ui_destroy` | 指针槽 `0x200d1634`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.alarm.time.ui_create` | 闹钟时间选择页面：UI 创建回调 | `word3` | `apps_alarm_time_ui_create` | 指针槽 `0x200d1690`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.alarm.time.ui_destroy` | 闹钟时间选择页面：UI 销毁回调 | `void1` | `apps_alarm_time_ui_destroy` | 指针槽 `0x200d16a8`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.media.volume.minus_icon` | 音量页：减小图标 | `void2` | `lv_image_set_src` | 调用点 `0xc51eeb4`，关闭对应页面后安装或卸载 | [media-volume-actions-043.json](../evidence/media-volume-actions-043.json) |
| `apps.media.volume.plus_icon` | 音量页：增大图标 | `void2` | `lv_image_set_src` | 调用点 `0xc51ef10`，关闭对应页面后安装或卸载 | [media-volume-actions-043.json](../evidence/media-volume-actions-043.json) |
| `apps.media.volume.minus_register` | 音量页：减小事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc51eef8`，关闭对应页面后安装或卸载 | [media-volume-actions-043.json](../evidence/media-volume-actions-043.json) |
| `apps.media.volume.plus_register` | 音量页：增大事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc51ef52`，关闭对应页面后安装或卸载 | [media-volume-actions-043.json](../evidence/media-volume-actions-043.json) |
| `apps.media.volume.bar_icon` | 音量页：从零恢复时的音量条 | `void2` | `lv_image_set_src` | 调用点 `0xc51e3fc`，关闭对应页面后安装或卸载 | [media-volume-actions-043.json](../evidence/media-volume-actions-043.json) |
| `apps.media.volume.ui_create` | 媒体音量页面：UI 创建回调 | `void3` | `apps_media_volume_ui_create` | 指针槽 `0x200d0ef8`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.media.volume.ui_destroy` | 媒体音量页面：UI 销毁回调 | `void1` | `apps_media_volume_ui_destroy` | 指针槽 `0x200d0f10`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.timer.preset_register` | 计时器主页：预设时间入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4ffbe4`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.add_register` | 计时器主页：自定义入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4ffd72`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.mask_icon` | 计时器主页：渐变遮罩 | `void2` | `lv_image_set_src` | 调用点 `0xc4ffd1c`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.add_icon` | 计时器主页：添加图标 | `void2` | `lv_image_set_src` | 调用点 `0xc4ffd50`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.plus_icon` | 计时器主页：加号图标 | `void2` | `lv_image_set_src` | 调用点 `0xc4ffd8c`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.custom.hours_event11` | 自定义页：小时滚轮事件 11 注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5015da`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.custom.minutes_event11` | 自定义页：分钟滚轮事件 11 注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5015e8`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.custom.seconds_event11` | 自定义页：秒滚轮事件 11 注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5015f6`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.custom.hours_event12` | 自定义页：小时滚轮事件 12 注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc501604`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.custom.minutes_event12` | 自定义页：分钟滚轮事件 12 注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc501612`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.custom.seconds_event12` | 自定义页：秒滚轮事件 12 注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc501620`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.custom.picker_event_code` | 自定义页：滚轮事件类型读取 | `word1` | `lv_event_get_code` | 调用点 `0xc5010a2`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.custom.colon_icon` | 自定义页：时间分隔图标 | `void2` | `lv_image_set_src` | 调用点 `0xc501516`、`0xc50153a`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.custom.top_shadow` | 自定义页：上方遮罩 | `void2` | `lv_image_set_src` | 调用点 `0xc50155e`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.custom.bottom_shadow` | 自定义页：下方遮罩 | `void2` | `lv_image_set_src` | 调用点 `0xc501590`，关闭对应页面后安装或卸载 | [timer-more-actions-043.json](../evidence/timer-more-actions-043.json) |
| `apps.timer.recent_register` | 最近使用项：注册启动回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4ffa14`，关闭对应界面后安装或卸载 | [timer-run-actions-043.json](../evidence/timer-run-actions-043.json) |
| `apps.timer.recent_hm_unit` | 最近使用项：小时或分钟单位 | `void2` | `lvx_label_set_text` | 调用点 `0xc4ff89a`，关闭对应界面后安装或卸载 | [timer-run-actions-043.json](../evidence/timer-run-actions-043.json) |
| `apps.timer.recent_seconds_unit` | 最近使用项：秒单位 | `void2` | `lvx_label_set_text` | 调用点 `0xc4ffa7a`，关闭对应界面后安装或卸载 | [timer-run-actions-043.json](../evidence/timer-run-actions-043.json) |
| `apps.timer.run.stop_register` | 运行视图：停止按钮事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc500af8`，关闭对应界面后安装或卸载 | [timer-run-actions-043.json](../evidence/timer-run-actions-043.json) |
| `apps.timer.run.toggle_register` | 运行视图：暂停或继续按钮事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc500b32`，关闭对应界面后安装或卸载 | [timer-run-actions-043.json](../evidence/timer-run-actions-043.json) |
| `apps.timer.run.stop_event_code` | 运行视图：停止按钮读取事件类型 | `word1` | `lv_event_get_code` | 调用点 `0xc50051c`，关闭对应界面后安装或卸载 | [timer-run-actions-043.json](../evidence/timer-run-actions-043.json) |
| `apps.timer.run.toggle_event_code` | 运行视图：暂停或继续按钮读取事件类型 | `word1` | `lv_event_get_code` | 调用点 `0xc500830`，关闭对应界面后安装或卸载 | [timer-run-actions-043.json](../evidence/timer-run-actions-043.json) |
| `apps.timer.done.caption` | 结束提示：结束文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4ff118`，关闭对应界面后安装或卸载 | [timer-run-actions-043.json](../evidence/timer-run-actions-043.json) |
| `apps.timer.run.initial_hide` | 计时器运行视图初建：添加标志 1 | `void2` | `lv_obj_add_flag` | 调用点 `0xc4ffec2`，关闭计时器主页后安装或卸载 | [timer-view-actions-043.json](../evidence/timer-view-actions-043.json) |
| `apps.timer.run.initial_clear_flag16` | 计时器运行视图初建：清除标志 16 | `void2` | `lv_obj_clear_flag` | 调用点 `0xc4ffeba`，关闭计时器主页后安装或卸载 | [timer-view-actions-043.json](../evidence/timer-view-actions-043.json) |
| `apps.timer.run.show` | 计时器切换至运行视图：清除标志 1 | `void2` | `lv_obj_clear_flag` | 调用点 `0xc4ffe80`，关闭计时器主页后安装或卸载 | [timer-view-actions-043.json](../evidence/timer-view-actions-043.json) |
| `apps.timer.main.hide` | 计时器切换至运行视图：主页添加标志 1 | `void2` | `lv_obj_add_flag` | 调用点 `0xc4ffe8a`，关闭计时器主页后安装或卸载 | [timer-view-actions-043.json](../evidence/timer-view-actions-043.json) |
| `apps.timer.main.clear_flag16` | 计时器切换至运行视图：主页清除标志 16 | `void2` | `lv_obj_clear_flag` | 调用点 `0xc4ffe94`，关闭计时器主页后安装或卸载 | [timer-view-actions-043.json](../evidence/timer-view-actions-043.json) |
| `apps.timer.run.hide` | 计时器返回主页：运行视图添加标志 1 | `void2` | `lv_obj_add_flag` | 调用点 `0xc4fff8a`，关闭计时器主页后安装或卸载 | [timer-view-actions-043.json](../evidence/timer-view-actions-043.json) |
| `apps.timer.main.show` | 计时器返回主页：主页清除标志 1 | `void2` | `lv_obj_clear_flag` | 调用点 `0xc4fff94`，关闭计时器主页后安装或卸载 | [timer-view-actions-043.json](../evidence/timer-view-actions-043.json) |
| `apps.timer.main.add_flag16` | 计时器返回主页：主页添加标志 16 | `void2` | `lv_obj_add_flag` | 调用点 `0xc4fff9e`，关闭计时器主页后安装或卸载 | [timer-view-actions-043.json](../evidence/timer-view-actions-043.json) |
| `apps.timer.recent_caption_refresh` | 计时器主页刷新：最近使用标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc5001a2`，关闭计时器主页后安装或卸载 | [timer-view-actions-043.json](../evidence/timer-view-actions-043.json) |
| `apps.timer.custom.ui_create` | 计时器自定义时间页面：UI 创建回调 | `word3` | `apps_timer_custom_ui_create` | 指针槽 `0x200d03dc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.timer.custom.ui_destroy` | 计时器自定义时间页面：UI 销毁回调 | `void1` | `apps_timer_custom_ui_destroy` | 指针槽 `0x200d03f4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.screenshot.ui_create` | 截屏设置页面：UI 创建回调 | `void3` | `settings_screenshot_ui_create` | 指针槽 `0x200d3ccc`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.screenshot.ui_destroy` | 截屏设置页面：UI 销毁回调 | `void1` | `settings_screenshot_ui_destroy` | 指针槽 `0x200d3ce4`，关闭对应页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.screenshot.toggle_register` | 截屏设置：开关事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc56f002`，关闭对应页面后安装或卸载 | [screenshot-settings-043.json](../evidence/screenshot-settings-043.json) |
| `settings.screenshot.event_code` | 截屏设置：开关读取事件类型 | `word1` | `lv_event_get_code` | 调用点 `0xc56f0ba`，关闭对应页面后安装或卸载 | [screenshot-settings-043.json](../evidence/screenshot-settings-043.json) |
| `settings.screenshot.event_data` | 截屏设置：开关读取事件数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc56f0c6`，关闭对应页面后安装或卸载 | [screenshot-settings-043.json](../evidence/screenshot-settings-043.json) |
| `settings.screenshot.description` | 截屏设置：说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc56f030`，关闭对应页面后安装或卸载 | [screenshot-settings-043.json](../evidence/screenshot-settings-043.json) |
| `health.oxygen.explanation.ui_create` | 血氧说明页面：UI 创建回调 | `word3` | `health_oxygen_explanation_ui_create` | 指针槽 `0x200db438`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.oxygen.explanation.ui_destroy` | 血氧说明页面：UI 销毁回调 | `void1` | `health_oxygen_explanation_ui_destroy` | 指针槽 `0x200db450`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.oxygen.explanation.intro` | 血氧说明：介绍 | `void2` | `lvx_label_set_text` | 调用点 `0xc649156`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.saturation1` | 血氧说明：血氧饱和度说明 1 | `void2` | `lvx_label_set_text` | 调用点 `0xc6491a2`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.saturation2` | 血氧说明：血氧饱和度说明 2 | `void2` | `lvx_label_set_text` | 调用点 `0xc6491e8`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.saturation3` | 血氧说明：血氧饱和度说明 3 | `void2` | `lvx_label_set_text` | 调用点 `0xc649236`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.measure_title` | 血氧说明：测量说明标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc64928e`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.measure_nb1` | 血氧说明：测量提示 1 | `void2` | `lvx_label_set_text` | 调用点 `0xc6492ee`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.measure_nb2` | 血氧说明：测量提示 2 | `void2` | `lvx_label_set_text` | 调用点 `0xc649380`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.measure6_intro` | 血氧说明：测量提示 6 | `void2` | `lvx_label_set_text` | 调用点 `0xc6493fc`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.low1` | 血氧说明：低值说明 1 | `void2` | `lvx_label_set_text` | 调用点 `0xc6494cc`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.low2` | 血氧说明：低值说明 2 | `void2` | `lvx_label_set_text` | 调用点 `0xc649510`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.low4` | 血氧说明：低值说明 4 | `void2` | `lvx_label_set_text` | 调用点 `0xc649550`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.measure1` | 血氧说明：测量说明 1 | `void2` | `lvx_label_set_text` | 调用点 `0xc649634`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.measure2` | 血氧说明：测量说明 2 | `void2` | `lvx_label_set_text` | 调用点 `0xc6496b2`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.measure5` | 血氧说明：测量说明 5 | `void2` | `lvx_label_set_text` | 调用点 `0xc64970c`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.measure6` | 血氧说明：测量说明 6 | `void2` | `lvx_label_set_text` | 调用点 `0xc649766`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.intro_wear1` | 血氧说明：血氧介绍：佩戴示意 1 | `void2` | `lv_image_set_src` | 调用点 `0xc649324`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.intro_wear2` | 血氧说明：血氧介绍：佩戴示意 2 | `void2` | `lv_image_set_src` | 调用点 `0xc6493a0`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.measure_wear1` | 血氧说明：测量说明：佩戴示意 1 | `void2` | `lv_image_set_src` | 调用点 `0xc6495d2`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `health.oxygen.explanation.measure_wear2` | 血氧说明：测量说明：佩戴示意 2 | `void2` | `lv_image_set_src` | 调用点 `0xc649658`，关闭对应页面后安装或卸载 | [oxygen-explanation-043.json](../evidence/oxygen-explanation-043.json) |
| `settings.gnss.ui_create` | 定位模式设置页面：UI 创建回调 | `word3` | `settings_gnss_ui_create` | 指针槽 `0x200d3084`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.gnss.ui_destroy` | 定位模式设置页面：UI 销毁回调 | `void1` | `settings_gnss_ui_destroy` | 指针槽 `0x200d309c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.gnss.row_register` | 定位模式设置：模式选项行事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc55e204`，关闭页面后安装或卸载 | [gnss-settings-043.json](../evidence/gnss-settings-043.json) |
| `settings.gnss.radio_register` | 定位模式设置：模式单选控件事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc55e258`，关闭页面后安装或卸载 | [gnss-settings-043.json](../evidence/gnss-settings-043.json) |
| `settings.gnss.event_code` | 定位模式设置：读取选项事件类型 | `word1` | `lv_event_get_code` | 调用点 `0xc55e3a4`，关闭页面后安装或卸载 | [gnss-settings-043.json](../evidence/gnss-settings-043.json) |
| `settings.gnss.event_data` | 定位模式设置：读取选项编号 | `word1` | `lv_event_get_user_data` | 调用点 `0xc55e3b4`，关闭页面后安装或卸载 | [gnss-settings-043.json](../evidence/gnss-settings-043.json) |
| `settings.gnss.info_clear_flag` | 定位模式设置：说明项清除标志 2 | `void2` | `lv_obj_clear_flag` | 调用点 `0xc55e290`，关闭页面后安装或卸载 | [gnss-settings-043.json](../evidence/gnss-settings-043.json) |
| `settings.wear.ui_create` | 佩戴方向设置页面：UI 创建回调 | `word3` | `settings_wear_ui_create` | 指针槽 `0x200d43b4`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.wear.ui_destroy` | 佩戴方向设置页面：UI 销毁回调 | `void1` | `settings_wear_ui_destroy` | 指针槽 `0x200d43cc`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.wear.left_wrist_register` | 佩戴方向设置：左手选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc572708`，关闭页面后安装或卸载 | [wear-settings-043.json](../evidence/wear-settings-043.json) |
| `settings.wear.right_wrist_register` | 佩戴方向设置：右手选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc572768`，关闭页面后安装或卸载 | [wear-settings-043.json](../evidence/wear-settings-043.json) |
| `settings.wear.left_crown_register` | 佩戴方向设置：左侧表冠选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc572834`，关闭页面后安装或卸载 | [wear-settings-043.json](../evidence/wear-settings-043.json) |
| `settings.wear.right_crown_register` | 佩戴方向设置：右侧表冠选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc572894`，关闭页面后安装或卸载 | [wear-settings-043.json](../evidence/wear-settings-043.json) |
| `settings.wear.event_code` | 佩戴方向设置：读取选项事件类型 | `word1` | `lv_event_get_code` | 调用点 `0xc57243c`，关闭页面后安装或卸载 | [wear-settings-043.json](../evidence/wear-settings-043.json) |
| `settings.wear.event_data` | 佩戴方向设置：读取选项编号 | `word1` | `lv_event_get_user_data` | 调用点 `0xc572444`，关闭页面后安装或卸载 | [wear-settings-043.json](../evidence/wear-settings-043.json) |
| `settings.wear.wrist_caption` | 佩戴方向设置：手腕分组文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc57268c`，关闭页面后安装或卸载 | [wear-settings-043.json](../evidence/wear-settings-043.json) |
| `settings.wear.crown_caption` | 佩戴方向设置：表冠分组文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5727b4`，关闭页面后安装或卸载 | [wear-settings-043.json](../evidence/wear-settings-043.json) |
| `home.main.ui_create` | 主屏主页：UI 创建回调 | `word3` | `home_main_ui_create` | 指针槽 `0x200d0994`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.main.ui_destroy` | 主屏主页：UI 销毁回调 | `void1` | `home_main_ui_destroy` | 指针槽 `0x200d09ac`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.edit.ui_create` | 主屏卡片编辑页面：UI 创建回调 | `word3` | `home_edit_ui_create` | 指针槽 `0x200d0914`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.edit.ui_destroy` | 主屏卡片编辑页面：UI 销毁回调 | `void1` | `home_edit_ui_destroy` | 指针槽 `0x200d092c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.add.ui_create` | 主屏卡片添加页面：UI 创建回调 | `word3` | `home_add_ui_create` | 指针槽 `0x200d0894`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.add.ui_destroy` | 主屏卡片添加页面：UI 销毁回调 | `void1` | `home_add_ui_destroy` | 指针槽 `0x200d08ac`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.main.scroll0_register` | 主屏滚动容器 0 事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc50b200`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.main.scroll1_register` | 主屏滚动容器 1 事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc50b220`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.main.scroll2_register` | 主屏滚动容器 2 事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc50b23e`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.main.scroll3_register` | 主屏滚动容器 3 事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc50b25a`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.edit.add_register` | 编辑页添加按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc50dc9e`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.edit.confirm_register` | 编辑页确认按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc50dd66`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.edit.event_code` | 编辑页回调读取事件类型 | `word1` | `lv_event_get_code` | 调用点 `0xc50e2fc`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.edit.event_data` | 编辑页回调读取操作编号 | `word1` | `lv_event_get_user_data` | 调用点 `0xc50e304`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.edit.add_icon` | 编辑页添加按钮图标 | `void2` | `lv_image_set_src` | 调用点 `0xc50dcbc`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.edit.shadow` | 编辑页按钮底部遮罩 | `void2` | `lv_image_set_src` | 调用点 `0xc50dd06`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.add.item_name` | 添加页卡片名称 | `void2` | `lvx_label_set_text` | 调用点 `0xc50d3a8`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.add.item_icon` | 添加页卡片图标 | `void2` | `lv_image_set_src` | 调用点 `0xc50d410`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.add.item_register` | 添加页卡片按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc50d45c`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.add.event_code` | 添加页回调读取事件类型 | `word1` | `lv_event_get_code` | 调用点 `0xc50d13e`，关闭页面后安装或卸载 | [home-pages-043.json](../evidence/home-pages-043.json) |
| `home.layout.ui_create` | 主屏布局选择页面：UI 创建回调 | `word3` | `home_layout_ui_create` | 指针槽 `0x200d0b20`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.layout.ui_destroy` | 主屏布局选择页面：UI 销毁回调 | `void1` | `home_layout_ui_destroy` | 指针槽 `0x200d0b38`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.pick.ui_create` | 主屏卡片挑选页面：UI 创建回调 | `word3` | `home_pick_ui_create` | 指针槽 `0x200d0a0c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.pick.ui_destroy` | 主屏卡片挑选页面：UI 销毁回调 | `void1` | `home_pick_ui_destroy` | 指针槽 `0x200d0a24`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.category.ui_create` | 主屏运动分类页面：UI 创建回调 | `word3` | `home_category_ui_create` | 指针槽 `0x200d0c08`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.category.ui_destroy` | 主屏运动分类页面：UI 销毁回调 | `void1` | `home_category_ui_destroy` | 指针槽 `0x200d0c20`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.sport.ui_create` | 主屏运动选择页面：UI 创建回调 | `word3` | `home_sport_ui_create` | 指针槽 `0x200d0b94`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.sport.ui_destroy` | 主屏运动选择页面：UI 销毁回调 | `void1` | `home_sport_ui_destroy` | 指针槽 `0x200d0bac`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.choose.ui_create` | 主屏卡片选择页面：UI 创建回调 | `word3` | `home_choose_ui_create` | 指针槽 `0x200d0aa0`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.choose.ui_destroy` | 主屏卡片选择页面：UI 销毁回调 | `void1` | `home_choose_ui_destroy` | 指针槽 `0x200d0ab8`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `home.layout.option_register` | 布局选项事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc511ff8`，关闭页面后安装或卸载 | [home-more-pages-043.json](../evidence/home-more-pages-043.json) |
| `home.layout.event_code` | 布局回调读取事件类型 | `word1` | `lv_event_get_code` | 调用点 `0xc511ef0`，关闭页面后安装或卸载 | [home-more-pages-043.json](../evidence/home-more-pages-043.json) |
| `home.layout.event_data` | 布局回调读取选项数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc511f08`，关闭页面后安装或卸载 | [home-more-pages-043.json](../evidence/home-more-pages-043.json) |
| `home.choose.item_register` | 卡片选择项事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5119c6`，关闭页面后安装或卸载 | [home-more-pages-043.json](../evidence/home-more-pages-043.json) |
| `home.choose.item_name` | 卡片选择项名称 | `void2` | `lvx_label_set_text` | 调用点 `0xc511a3a`，关闭页面后安装或卸载 | [home-more-pages-043.json](../evidence/home-more-pages-043.json) |
| `home.choose.calendar_icon` | 日历卡片预览图 | `void2` | `lv_image_set_src` | 调用点 `0xc511bb4`，关闭页面后安装或卸载 | [home-more-pages-043.json](../evidence/home-more-pages-043.json) |
| `home.choose.calendar_day` | 日历卡片日期 | `void2` | `lvx_label_set_text` | 调用点 `0xc511c80`，关闭页面后安装或卸载 | [home-more-pages-043.json](../evidence/home-more-pages-043.json) |
| `home.choose.calendar_weekday` | 日历卡片星期 | `void2` | `lvx_label_set_text` | 调用点 `0xc511c8a`，关闭页面后安装或卸载 | [home-more-pages-043.json](../evidence/home-more-pages-043.json) |
| `home.choose.calendar_preview` | 日历卡片快照图 | `void2` | `lv_image_set_src` | 调用点 `0xc511d7c`，关闭页面后安装或卸载 | [home-more-pages-043.json](../evidence/home-more-pages-043.json) |
| `settings.display.timeout.ui_create` | 熄屏时间设置页面：UI 创建回调 | `word3` | `settings_display_timeout_ui_create` | 指针槽 `0x200d2a6c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.timeout.ui_destroy` | 熄屏时间设置页面：UI 销毁回调 | `void1` | `settings_display_timeout_ui_destroy` | 指针槽 `0x200d2a84`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.keep_awake.ui_create` | 屏幕常亮设置页面：UI 创建回调 | `word3` | `settings_display_keep_awake_ui_create` | 指针槽 `0x200d290c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.keep_awake.ui_destroy` | 屏幕常亮设置页面：UI 销毁回调 | `void1` | `settings_display_keep_awake_ui_destroy` | 指针槽 `0x200d2924`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.timeout.top_icon` | 熄屏时间：上方图标 | `void2` | `lv_image_set_src` | 调用点 `0xc557dee`，关闭页面后安装或卸载 | [display-time-settings-043.json](../evidence/display-time-settings-043.json) |
| `settings.display.timeout.bottom_icon` | 熄屏时间：下方图标 | `void2` | `lv_image_set_src` | 调用点 `0xc557e16`，关闭页面后安装或卸载 | [display-time-settings-043.json](../evidence/display-time-settings-043.json) |
| `settings.display.timeout.seconds_caption` | 熄屏时间：秒单位文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc557e4e`，关闭页面后安装或卸载 | [display-time-settings-043.json](../evidence/display-time-settings-043.json) |
| `settings.display.timeout.top_shadow` | 熄屏时间：上方遮罩 | `void2` | `lv_image_set_src` | 调用点 `0xc557e7a`，关闭页面后安装或卸载 | [display-time-settings-043.json](../evidence/display-time-settings-043.json) |
| `settings.display.timeout.bottom_shadow` | 熄屏时间：下方遮罩 | `void2` | `lv_image_set_src` | 调用点 `0xc557ea0`，关闭页面后安装或卸载 | [display-time-settings-043.json](../evidence/display-time-settings-043.json) |
| `settings.display.timeout.confirm_event` | 熄屏时间：确认回调事件类型 | `word1` | `lv_event_get_code` | 调用点 `0xc557ce0`，关闭页面后安装或卸载 | [display-time-settings-043.json](../evidence/display-time-settings-043.json) |
| `settings.display.keep_awake.off_register` | 屏幕常亮：关闭选项事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc555dde`，关闭页面后安装或卸载 | [display-time-settings-043.json](../evidence/display-time-settings-043.json) |
| `settings.display.keep_awake.duration_register` | 屏幕常亮：时长选项事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc555d20`，关闭页面后安装或卸载 | [display-time-settings-043.json](../evidence/display-time-settings-043.json) |
| `settings.display.keep_awake.event_data` | 屏幕常亮：读取选项数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc555ac6`，关闭页面后安装或卸载 | [display-time-settings-043.json](../evidence/display-time-settings-043.json) |
| `settings.display.keep_awake.event_target` | 屏幕常亮：读取当前目标 | `word1` | `lv_event_current_target` | 调用点 `0xc555ace`，关闭页面后安装或卸载 | [display-time-settings-043.json](../evidence/display-time-settings-043.json) |
| `settings.display.raise_mode.ui_create` | 抬腕显示方式页面：UI 创建回调 | `word3` | `settings_display_raise_mode_ui_create` | 指针槽 `0x200d2984`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.raise_mode.ui_destroy` | 抬腕显示方式页面：UI 销毁回调 | `void1` | `settings_display_raise_mode_ui_destroy` | 指针槽 `0x200d299c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.raise_schedule.ui_create` | 抬腕亮屏时段页面：UI 创建回调 | `word3` | `settings_display_raise_schedule_ui_create` | 指针槽 `0x200d2af4`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.raise_schedule.ui_destroy` | 抬腕亮屏时段页面：UI 销毁回调 | `void1` | `settings_display_raise_schedule_ui_destroy` | 指针槽 `0x200d2b0c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.aod_schedule.ui_create` | 息屏显示时段页面：UI 创建回调 | `word3` | `settings_display_aod_schedule_ui_create` | 指针槽 `0x200d29f8`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.aod_schedule.ui_destroy` | 息屏显示时段页面：UI 销毁回调 | `void1` | `settings_display_aod_schedule_ui_destroy` | 指针槽 `0x200d2a10`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.raise_mode.dial_register` | 抬腕显示：表盘方式注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc556344`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.raise_mode.wrist_register` | 抬腕显示：抬腕方式注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5563d8`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.raise_mode.event_code` | 抬腕显示：事件类型 | `word1` | `lv_event_get_code` | 调用点 `0xc55658e`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.raise_mode.event_data` | 抬腕显示：选项数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc556598`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.raise_schedule.mode_register` | 抬腕亮屏时段：模式选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5592ba`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.raise_schedule.time_register` | 抬腕亮屏时段：时间选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5593d4`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.raise_schedule.mode_data` | 抬腕亮屏时段：模式数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc5583f0`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.raise_schedule.time_data` | 抬腕亮屏时段：时间选项数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc558756`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.aod_schedule.mode_register` | 息屏显示时段：模式选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5577b2`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.aod_schedule.timed_register` | 息屏显示时段：定时选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc557894`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.aod_schedule.time_register` | 息屏显示时段：时间选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5579ba`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.aod_schedule.mode_data` | 息屏显示时段：模式数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc556e9c`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.aod_schedule.reminder` | 息屏显示时段：说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc557822`，关闭页面后安装或卸载 | [display-schedules-043.json](../evidence/display-schedules-043.json) |
| `settings.display.main.ui_create` | 显示设置主页：UI 创建回调 | `word3` | `settings_display_main_ui_create` | 指针槽 `0x200d273c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.main.ui_destroy` | 显示设置主页：UI 销毁回调 | `void1` | `settings_display_main_ui_destroy` | 指针槽 `0x200d2754`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.aod_detail.ui_create` | 息屏显示详细设置页面：UI 创建回调 | `word3` | `settings_display_aod_detail_ui_create` | 指针槽 `0x200d27b0`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.aod_detail.ui_destroy` | 息屏显示详细设置页面：UI 销毁回调 | `void1` | `settings_display_aod_detail_ui_destroy` | 指针槽 `0x200d27c8`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.aod_switch.ui_create` | 息屏显示开关页面：UI 创建回调 | `word3` | `settings_display_aod_switch_ui_create` | 指针槽 `0x200d2824`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.aod_switch.ui_destroy` | 息屏显示开关页面：UI 销毁回调 | `void1` | `settings_display_aod_switch_ui_destroy` | 指针槽 `0x200d283c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.display.main.brightness_register` | 显示主页：亮度入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc552bc0`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.main.timeout_register` | 显示主页：熄屏时间入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc552c26`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.main.wrist_register` | 显示主页：抬腕亮屏入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc552d36`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.main.aod_register` | 显示主页：息屏显示入口 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc552da0`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.main.event_data` | 显示主页：读取入口编号 | `word1` | `lv_event_get_user_data` | 调用点 `0xc552a32`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.main.timeout_caption` | 显示主页：熄屏时间说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc552c84`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.aod_detail.switch_register` | 息屏详情：总开关注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5538e2`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.aod_detail.wrist_register` | 息屏详情：抬腕选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc553940`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.aod_detail.timed_register` | 息屏详情：定时开关注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5539c0`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.aod_detail.start_register` | 息屏详情：开始时间注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc553a50`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.aod_detail.end_register` | 息屏详情：结束时间注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc553b34`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.aod_detail.dial_register` | 息屏详情：表盘入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc553bbc`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.aod_detail.event_data` | 息屏详情：读取操作编号 | `word1` | `lv_event_get_user_data` | 调用点 `0xc554036`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.aod_detail.dial_info` | 息屏详情：表盘说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc553be0`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.aod_detail.wrist_info` | 息屏详情：抬腕说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc553cd4`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.aod_switch.register` | 息屏开关页：开关事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5548fa`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `settings.display.aod_switch.event_data` | 息屏开关页：读取操作编号 | `word1` | `lv_event_get_user_data` | 调用点 `0xc55476a`，关闭页面后安装或卸载 | [display-main-043.json](../evidence/display-main-043.json) |
| `apps.recorder.upload.ui_create` | 录音上传页面：UI 创建回调 | `word3` | `apps_recorder_upload_ui_create` | 指针槽 `0x200da6c4`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.recorder.upload.ui_destroy` | 录音上传页面：UI 销毁回调 | `void1` | `apps_recorder_upload_ui_destroy` | 指针槽 `0x200da6dc`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.recorder.remind.ui_create` | 录音上传提醒页面：UI 创建回调 | `word3` | `apps_recorder_remind_ui_create` | 指针槽 `0x200da650`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.recorder.remind.ui_destroy` | 录音上传提醒页面：UI 销毁回调 | `void1` | `apps_recorder_remind_ui_destroy` | 指针槽 `0x200da668`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.recorder.interrupt.ui_create` | 录音中断页面：UI 创建回调 | `word3` | `apps_recorder_interrupt_ui_create` | 指针槽 `0x200da564`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.recorder.interrupt.ui_destroy` | 录音中断页面：UI 销毁回调 | `void1` | `apps_recorder_interrupt_ui_destroy` | 指针槽 `0x200da57c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.recorder.start_register` | 录音主页：开始按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc61aa2a`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.button_data` | 录音主页：读取按钮操作编号 | `word1` | `lv_event_get_user_data` | 调用点 `0xc61ad90`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.empty_icon` | 录音主页：空列表图标 | `void2` | `lv_image_set_src` | 调用点 `0xc6195ea`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.empty_caption` | 录音主页：空列表说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc619628`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.upload.percent` | 录音上传：百分号 | `void2` | `lvx_label_set_text` | 调用点 `0xc61bcfe`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.upload.exit_register` | 录音上传：退出操作注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc61bf44`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.upload.resume_register` | 录音上传：恢复视图注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc61be6e`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.upload.exit_caption` | 录音上传：退出说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc61bf7e`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.upload.continue_caption` | 录音上传：继续说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc61bff8`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.upload.fail_icon` | 录音上传：失败图标 | `void2` | `lv_image_set_src` | 调用点 `0xc61c0a6`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.remind.sync_caption` | 上传提醒：同步说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc61b68c`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.remind.goto_caption` | 上传提醒：跳转说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc61b6e4`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.remind.sync_icon` | 上传提醒：未同步图标 | `void2` | `lv_image_set_src` | 调用点 `0xc61b69c`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.remind.finish_register` | 上传提醒：完成按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc61b778`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.remind.disable_register` | 上传提醒：不再提醒按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc61b80a`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.interrupt.fail_icon` | 录音中断：失败图标 | `void2` | `lv_image_set_src` | 调用点 `0xc618976`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.interrupt.caption` | 录音中断：中断说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc618996`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.interrupt.know_register` | 录音中断：确认按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc618a58`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.interrupt.bt_caption` | 录音中断：连接失败说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc618872`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `apps.recorder.interrupt.bt_register` | 录音中断：连接提示注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc61890a`，关闭页面后安装或卸载 | [recorder-pages-043.json](../evidence/recorder-pages-043.json) |
| `health.vitality.setting.ui_create` | 活力设置页面：UI 创建回调 | `word3` | `health_vitality_setting_ui_create` | 指针槽 `0x200db840`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.vitality.setting.ui_destroy` | 活力设置页面：UI 销毁回调 | `void1` | `health_vitality_setting_ui_destroy` | 指针槽 `0x200db858`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.vitality.explanation.ui_create` | 活力说明页面：UI 创建回调 | `word3` | `health_vitality_explanation_ui_create` | 指针槽 `0x200db728`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.vitality.explanation.ui_destroy` | 活力说明页面：UI 销毁回调 | `void1` | `health_vitality_explanation_ui_destroy` | 指针槽 `0x200db740`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.vitality.hr_catalog.ui_create` | 活力中的心率设置目录页面：UI 创建回调 | `void3` | `health_vitality_hr_catalog_ui_create` | 指针槽 `0x200dc0b0`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.vitality.hr_catalog.ui_destroy` | 活力中的心率设置目录页面：UI 销毁回调 | `void1` | `health_vitality_hr_catalog_ui_destroy` | 指针槽 `0x200dc0c8`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.vitality.weekly_caption` | 活力主页：周进度说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc64ffac`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.weekly_value_caption` | 活力主页：周活力说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc65019c`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.today_icon` | 活力主页：今日图标 | `void2` | `lv_image_set_src` | 调用点 `0xc65028a`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.today_caption` | 活力主页：今日获得说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc6502ac`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.little_icon` | 活力主页：低强度图标 | `void2` | `lv_image_set_src` | 调用点 `0xc650352`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.little_caption` | 活力主页：低强度说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc650388`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.medium_icon` | 活力主页：中强度图标 | `void2` | `lv_image_set_src` | 调用点 `0xc65047a`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.medium_caption` | 活力主页：中强度说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc6504b4`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.large_icon` | 活力主页：高强度图标 | `void2` | `lv_image_set_src` | 调用点 `0xc650586`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.large_caption` | 活力主页：高强度说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc6505c0`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.setting_register` | 活力主页：设置入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc65078e`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.explanation_register` | 活力主页：说明入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc65082e`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.setting.option_register` | 活力设置：设置按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc650d14`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.setting.option_data` | 活力设置：读取设置编号 | `word1` | `lv_event_get_user_data` | 调用点 `0xc650bea`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.setting.next_icon` | 活力设置：箭头图标 | `void2` | `lv_image_set_src` | 调用点 `0xc650d2a`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.setting.description` | 活力设置：说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc650dbc`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.vitality.explanation.text` | 活力说明：说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc64f8be`，关闭页面后安装或卸载 | [vitality-pages-043.json](../evidence/vitality-pages-043.json) |
| `health.women.notes.ui_create` | 女性健康说明页面：UI 创建回调 | `word3` | `health_women_notes_ui_create` | 指针槽 `0x200da738`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.women.notes.ui_destroy` | 女性健康说明页面：UI 销毁回调 | `void1` | `health_women_notes_ui_destroy` | 指针槽 `0x200da750`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.women.notes.chart_caption` | 女性健康：说明页图表标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc620810`，关闭对应页面后安装或卸载 | [women-pages-043.json](../evidence/women-pages-043.json) |
| `health.women.notes.chart_description` | 女性健康：说明页图表正文 | `void2` | `lvx_label_set_text` | 调用点 `0xc620870`，关闭对应页面后安装或卸载 | [women-pages-043.json](../evidence/women-pages-043.json) |
| `health.women.notes.chart_notes` | 女性健康：说明页图表备注 | `void2` | `lvx_label_set_text` | 调用点 `0xc6208a2`，关闭对应页面后安装或卸载 | [women-pages-043.json](../evidence/women-pages-043.json) |
| `health.women.notes.legend_icon` | 女性健康：说明页图例图标（四项共用） | `void2` | `lv_image_set_src` | 调用点 `0xc6206e0`，关闭对应页面后安装或卸载 | [women-pages-043.json](../evidence/women-pages-043.json) |
| `health.women.notes.legend_caption` | 女性健康：说明页图例文字（四项共用） | `void2` | `lvx_label_set_text` | 调用点 `0xc620718`，关闭对应页面后安装或卸载 | [women-pages-043.json](../evidence/women-pages-043.json) |
| `health.women.notes.know_register` | 女性健康：说明页确认按钮回调注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc62090a`，关闭对应页面后安装或卸载 | [women-pages-043.json](../evidence/women-pages-043.json) |
| `health.women.empty_icon` | 女性健康：主页面无数据图标 | `void2` | `lv_image_set_src` | 调用点 `0xc6218be`，关闭对应页面后安装或卸载 | [women-pages-043.json](../evidence/women-pages-043.json) |
| `health.women.empty_caption` | 女性健康：主页面无数据文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc62191e`，关闭对应页面后安装或卸载 | [women-pages-043.json](../evidence/women-pages-043.json) |
| `health.women.main.left_icon` | 女性健康主页面：左箭头图标 | `void2` | `lv_image_set_src` | 调用点 `0xc6202c4`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.left_empty_icon` | 女性健康主页面：左箭头无数据图标 | `void2` | `lv_image_set_src` | 调用点 `0xc6202fc`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.right_icon` | 女性健康主页面：右箭头图标 | `void2` | `lv_image_set_src` | 调用点 `0xc62032a`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.right_empty_icon` | 女性健康主页面：右箭头无数据图标 | `void2` | `lv_image_set_src` | 调用点 `0xc62035e`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.left_register` | 女性健康主页面：左箭头事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc6202d8`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.right_register` | 女性健康主页面：右箭头事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc62033e`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.mark_register` | 女性健康主页面：标记按钮事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc6204ac`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_register` | 女性健康主页面：柱状图滚动事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc620d04`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_current_bar7` | 女性健康主页面：柱状图当前项 bar7 | `void2` | `lv_image_set_src` | 调用点 `0xc620d36`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_current_bar8` | 女性健康主页面：柱状图当前项 bar8 | `void2` | `lv_image_set_src` | 调用点 `0xc620e6c`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_current_bar9` | 女性健康主页面：柱状图当前项 bar9 | `void2` | `lv_image_set_src` | 调用点 `0xc620e76`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_current_bar6` | 女性健康主页面：柱状图当前项 bar6 | `void2` | `lv_image_set_src` | 调用点 `0xc620e7e`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_current_bar10` | 女性健康主页面：柱状图当前项 bar10 | `void2` | `lv_image_set_src` | 调用点 `0xc620ea8`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_next_bar2` | 女性健康主页面：柱状图后续项 bar2 | `void2` | `lv_image_set_src` | 调用点 `0xc620d8a`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_next_bar4` | 女性健康主页面：柱状图后续项 bar4 | `void2` | `lv_image_set_src` | 调用点 `0xc620dee`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_next_bar1` | 女性健康主页面：柱状图后续项 bar1 | `void2` | `lv_image_set_src` | 调用点 `0xc620df6`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_next_bar3` | 女性健康主页面：柱状图后续项 bar3 | `void2` | `lv_image_set_src` | 调用点 `0xc620dfe`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_previous_bar2_or4` | 女性健康主页面：柱状图前序项 bar2 或 bar4 | `void2` | `lv_image_set_src` | 调用点 `0xc620e08`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_previous_bar3` | 女性健康主页面：柱状图前序项 bar3 | `void2` | `lv_image_set_src` | 调用点 `0xc620e4e`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_previous_bar5` | 女性健康主页面：柱状图前序项 bar5 | `void2` | `lv_image_set_src` | 调用点 `0xc620e5c`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.pillar_previous_bar1` | 女性健康主页面：柱状图前序项 bar1 | `void2` | `lv_image_set_src` | 调用点 `0xc620e64`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.date_caption` | 女性健康主页面：主页面日期文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc6216e0`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.status_no_record` | 女性健康主页面：状态文字：今日无记录 | `void2` | `lvx_label_set_text` | 调用点 `0xc621842`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.status_ovulation_day` | 女性健康主页面：状态文字：排卵日 | `void2` | `lvx_label_set_text` | 调用点 `0xc621856`，关闭对应页面后安装或卸载 | [women-main-043.json](../evidence/women-main-043.json) |
| `health.women.main.reset_bar2` | 女性健康主页面：滚动后reset bar2 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620ab8`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.reset_bar4` | 女性健康主页面：滚动后reset bar4 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620ae8`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.reset_bar3` | 女性健康主页面：滚动后reset bar3 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620af0`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.reset_bar1` | 女性健康主页面：滚动后reset bar1 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620af8`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.reset_bar5` | 女性健康主页面：滚动后reset bar5 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620bc0`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.positive_bar8` | 女性健康主页面：滚动后positive bar8 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620b00`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.positive_bar7` | 女性健康主页面：滚动后positive bar7 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620b14`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.positive_bar9` | 女性健康主页面：滚动后positive bar9 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620b20`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.positive_bar6` | 女性健康主页面：滚动后positive bar6 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620b2c`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.nonpositive_bar8` | 女性健康主页面：滚动后nonpositive bar8 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620b68`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.nonpositive_bar6` | 女性健康主页面：滚动后nonpositive bar6 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620b7c`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.nonpositive_bar7` | 女性健康主页面：滚动后nonpositive bar7 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620b8a`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.nonpositive_bar9` | 女性健康主页面：滚动后nonpositive bar9 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620b9a`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.nonpositive_bar10` | 女性健康主页面：滚动后nonpositive bar10 图标 | `void2` | `lv_image_set_src` | 调用点 `0xc620bc8`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.left_event_code` | 女性健康主页面：左箭头事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc620096`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.left_event_data` | 女性健康主页面：左箭头事件数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc6200a2`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.right_event_code` | 女性健康主页面：右箭头事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc62005a`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.right_event_data` | 女性健康主页面：右箭头事件数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc620066`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.mark_event_data` | 女性健康主页面：标记按钮事件数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc620022`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.scroll_event_code` | 女性健康主页面：柱状图滚动事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc6209d6`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.scroll_event_target` | 女性健康主页面：柱状图滚动事件原始目标 | `word1` | `lv_event_original_target` | 调用点 `0xc6209de`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.women.main.scroll_event_data` | 女性健康主页面：柱状图滚动事件数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc6209e6`，关闭对应页面后安装或卸载 | [women-scroll-043.json](../evidence/women-scroll-043.json) |
| `health.sleep.explanation.ui_create` | 睡眠说明页面：UI 创建回调 | `word3` | `health_sleep_explanation_ui_create` | 指针槽 `0x200dafe4`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.explanation.ui_destroy` | 睡眠说明页面：UI 销毁回调 | `void1` | `health_sleep_explanation_ui_destroy` | 指针槽 `0x200daffc`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `health.sleep.explanation.instructions1` | 睡眠说明页面：说明第一段 | `void2` | `lvx_label_set_text` | 调用点 `0xc63be90`，关闭页面后安装或卸载 | [sleep-explanation-043.json](../evidence/sleep-explanation-043.json) |
| `health.sleep.explanation.instructions2` | 睡眠说明页面：说明第二段 | `void2` | `lvx_label_set_text` | 调用点 `0xc63bf04`，关闭页面后安装或卸载 | [sleep-explanation-043.json](../evidence/sleep-explanation-043.json) |
| `health.sleep.explanation.longshort` | 睡眠说明页面：长短睡眠说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc63bf74`，关闭页面后安装或卸载 | [sleep-explanation-043.json](../evidence/sleep-explanation-043.json) |
| `health.sleep.explanation.instructions3` | 睡眠说明页面：说明第三段 | `void2` | `lvx_label_set_text` | 调用点 `0xc63bfe2`，关闭页面后安装或卸载 | [sleep-explanation-043.json](../evidence/sleep-explanation-043.json) |
| `apps.worldclock.main.ui_create` | 世界时钟主页：UI 创建回调 | `word3` | `apps_worldclock_main_ui_create` | 指针槽 `0x200d9e98`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.worldclock.main.ui_destroy` | 世界时钟主页：UI 销毁回调 | `void1` | `apps_worldclock_main_ui_destroy` | 指针槽 `0x200d9eb0`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.worldclock.add_list.ui_create` | 世界时钟添加城市列表：UI 创建回调 | `word3` | `apps_worldclock_add_list_ui_create` | 指针槽 `0x200d9e24`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.worldclock.add_list.ui_destroy` | 世界时钟添加城市列表：UI 销毁回调 | `void1` | `apps_worldclock_add_list_ui_destroy` | 指针槽 `0x200d9e3c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.worldclock.detail.ui_create` | 世界时钟城市详情：UI 创建回调 | `word3` | `apps_worldclock_detail_ui_create` | 指针槽 `0x200d9db0`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.worldclock.detail.ui_destroy` | 世界时钟城市详情：UI 销毁回调 | `void1` | `apps_worldclock_detail_ui_destroy` | 指针槽 `0x200d9dc8`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.worldclock.main.empty_caption` | 世界时钟：主页无城市提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc601728`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.main.empty_add_icon` | 世界时钟：主页无城市时添加图标 | `void2` | `lv_image_set_src` | 调用点 `0xc601762`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.main.empty_icon` | 世界时钟：主页无城市图标 | `void2` | `lv_image_set_src` | 调用点 `0xc60179a`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.main.empty_add_register` | 世界时钟：主页无城市时添加事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc601784`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.main.single_add_icon` | 世界时钟：主页单城市时添加图标 | `void2` | `lv_image_set_src` | 调用点 `0xc6017f2`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.main.single_add_register` | 世界时钟：主页单城市时添加事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc601806`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.add_list.more_caption_create` | 世界时钟：城市列表更多提示创建 | `void2` | `lvx_label_set_text` | 调用点 `0xc6008a6`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.add_list.more_caption_update` | 世界时钟：城市列表更多提示更新 | `void2` | `lvx_label_set_text` | 调用点 `0xc600baa`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.add_list.city_register_create` | 世界时钟：城市列表事件注册创建 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc600928`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.add_list.city_register_update` | 世界时钟：城市列表事件注册更新 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc600c1a`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.detail.initial_time` | 世界时钟：详情首次时间文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc6001f2`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.detail.initial_weekday` | 世界时钟：详情首次星期文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc6001fc`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.detail.refresh_time` | 世界时钟：详情定时更新时间文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5fff56`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.detail.refresh_weekday` | 世界时钟：详情定时更新星期文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc5fff62`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.worldclock.detail.delete_register` | 世界时钟：详情删除按钮事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc6002a6`，关闭对应页面后安装或卸载 | [worldclock-043.json](../evidence/worldclock-043.json) |
| `apps.todolist.main.ui_create` | 待办事项主页：UI 创建回调 | `word3` | `apps_todolist_main_ui_create` | 指针槽 `0x200dcde4`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.todolist.main.ui_destroy` | 待办事项主页：UI 销毁回调 | `void1` | `apps_todolist_main_ui_destroy` | 指针槽 `0x200dcdfc`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.todolist.list.ui_create` | 待办事项列表：UI 创建回调 | `word3` | `apps_todolist_list_ui_create` | 指针槽 `0x200dcd70`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.todolist.list.ui_destroy` | 待办事项列表：UI 销毁回调 | `void1` | `apps_todolist_list_ui_destroy` | 指针槽 `0x200dcd88`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.todolist.detail.ui_create` | 待办事项详情：UI 创建回调 | `word3` | `apps_todolist_detail_ui_create` | 指针槽 `0x200dccfc`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.todolist.detail.ui_destroy` | 待办事项详情：UI 销毁回调 | `void1` | `apps_todolist_detail_ui_destroy` | 指针槽 `0x200dcd14`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.todolist.sub_list.ui_create` | 待办事项子列表：UI 创建回调 | `word3` | `apps_todolist_sub_list_ui_create` | 指针槽 `0x200dce58`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.todolist.sub_list.ui_destroy` | 待办事项子列表：UI 销毁回调 | `void1` | `apps_todolist_sub_list_ui_destroy` | 指针槽 `0x200dce70`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.todolist.detail.title_full` | 待办事项：详情未截断的事项文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc6813cc`，关闭对应页面后安装或卸载 | [todolist-043.json](../evidence/todolist-043.json) |
| `apps.todolist.detail.title_truncated` | 待办事项：详情截断的事项文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc6812ec`，关闭对应页面后安装或卸载 | [todolist-043.json](../evidence/todolist-043.json) |
| `apps.todolist.detail.status_register` | 待办事项：详情状态按钮事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc681376`，关闭对应页面后安装或卸载 | [todolist-043.json](../evidence/todolist-043.json) |
| `apps.todolist.list.row_checkbox_register` | 待办事项：列表行勾选控件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc681fee`，关闭对应页面后安装或卸载 | [todolist-043.json](../evidence/todolist-043.json) |
| `apps.todolist.list.row_register_ordinary` | 待办事项：列表普通行事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc6820f8`，关闭对应页面后安装或卸载 | [todolist-043.json](../evidence/todolist-043.json) |
| `apps.todolist.list.row_register_alternate` | 待办事项：列表另一分支行事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc68218e`，关闭对应页面后安装或卸载 | [todolist-043.json](../evidence/todolist-043.json) |
| `apps.todolist.list.row_due_icon` | 待办事项：列表到期状态图标 | `void2` | `lv_image_set_src` | 调用点 `0xc6824e8`，关闭对应页面后安装或卸载 | [todolist-043.json](../evidence/todolist-043.json) |
| `apps.todolist.sub_list.item_text` | 待办事项：子列表事项文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc683084`，关闭对应页面后安装或卸载 | [todolist-043.json](../evidence/todolist-043.json) |
| `apps.todolist.sub_list.checkbox_register_create` | 待办事项：子列表勾选控件创建时注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc683b2c`，关闭对应页面后安装或卸载 | [todolist-043.json](../evidence/todolist-043.json) |
| `apps.todolist.sub_list.row_register_create` | 待办事项：子列表行创建时注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc683ba8`，关闭对应页面后安装或卸载 | [todolist-043.json](../evidence/todolist-043.json) |
| `apps.todolist.sub_list.row_register_update` | 待办事项：子列表行更新时注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc683c5a`，关闭对应页面后安装或卸载 | [todolist-043.json](../evidence/todolist-043.json) |
| `apps.todolist.sub_list.checkbox_register_update` | 待办事项：子列表勾选控件更新时注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc683c6e`，关闭对应页面后安装或卸载 | [todolist-043.json](../evidence/todolist-043.json) |
| `apps.phonemute.ui_create` | 手机静音：UI 创建回调 | `word3` | `apps_phonemute_ui_create` | 指针槽 `0x200da8e4`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.phonemute.ui_destroy` | 手机静音：UI 销毁回调 | `void1` | `apps_phonemute_ui_destroy` | 指针槽 `0x200da8fc`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.find_phone.ui_create` | 查找手机：UI 创建回调 | `word3` | `apps_find_phone_ui_create` | 指针槽 `0x200da99c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.find_phone.ui_destroy` | 查找手机：UI 销毁回调 | `void1` | `apps_find_phone_ui_destroy` | 指针槽 `0x200da9b4`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.phonemute.disconnect_icon` | 蓝牙断连图标 | `void2` | `lv_image_set_src` | 调用点 `0xc624192`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.disconnect_text` | 蓝牙断连文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc6241de`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.retry_text` | 连接重试文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc62423e`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.disconnect_confirm_text` | 断连确认文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc6242d2`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.disconnect_confirm_register` | 断连确认按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc62429e`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.permission_text` | 权限提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc624348`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.permission_register` | 权限确认按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc6243e8`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.failure_icon` | 连接失败图标 | `void2` | `lv_image_set_src` | 调用点 `0xc624426`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.failure_text` | 连接失败文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc6244dc`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.failure_confirm_text` | 失败确认文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc62456e`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.failure_confirm_register` | 失败确认按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc62453a`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.muted_icon` | 静音状态图标 | `void2` | `lv_image_set_src` | 调用点 `0xc623ae0`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.ring_icon` | 响铃状态图标 | `void2` | `lv_image_set_src` | 调用点 `0xc623bca`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.mode_text` | 当前状态文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc623b10`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.mode_register` | 切换按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc623bbc`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.progress_text` | 切换中状态文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc623d4e`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.phonemute.toast_text` | 切换结果文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc623cca`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.find_phone.phone_icon` | 查找页面手机图标 | `void2` | `lv_image_set_src` | 调用点 `0xc624d60`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.find_phone.bell_text` | 查找页面提示文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc6250fa`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.find_phone.bluetooth_icon` | 蓝牙断连图标 | `void2` | `lv_image_set_src` | 调用点 `0xc624df8`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.find_phone.bluetooth_text` | 蓝牙断连文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc624e36`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.find_phone.retry_text` | 连接重试文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc624eae`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.find_phone.app_failure_icon` | 应用断连图标 | `void2` | `lv_image_set_src` | 调用点 `0xc624f7a`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.find_phone.app_failure_text` | 应用断连文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc624fc8`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `apps.find_phone.button_register` | 查找或确认按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc624a24`，关闭对应页面后安装或卸载 | [phone-utilities-043.json](../evidence/phone-utilities-043.json) |
| `settings.main.ui_create` | 设置主页：UI 创建回调 | `word3` | `settings_main_ui_create` | 指针槽 `0x200d34ec`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.main.ui_destroy` | 设置主页：UI 销毁回调 | `void1` | `settings_main_ui_destroy` | 指针槽 `0x200d3504`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.main.row_register_create` | 设置列表行创建时注册事件 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc566bfe`，关闭页面后安装或卸载 | [settings-main-043.json](../evidence/settings-main-043.json) |
| `settings.main.row_register_update` | 设置列表行更新时注册事件 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc566488`，关闭页面后安装或卸载 | [settings-main-043.json](../evidence/settings-main-043.json) |
| `settings.main.row_event_code` | 设置列表行事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc566554`，关闭页面后安装或卸载 | [settings-main-043.json](../evidence/settings-main-043.json) |
| `settings.main.row_index` | 设置列表行索引 | `word1` | `lv_event_get_user_data` | 调用点 `0xc566564`，关闭页面后安装或卸载 | [settings-main-043.json](../evidence/settings-main-043.json) |
| `settings.system.ui_create` | 系统设置页面：UI 创建回调 | `word3` | `settings_system_ui_create` | 指针槽 `0x200d3fb4`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.system.ui_destroy` | 系统设置页面：UI 销毁回调 | `void1` | `settings_system_ui_destroy` | 指针槽 `0x200d3fcc`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.system.row_register_create` | 系统设置行创建时注册事件 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc57121e`，关闭页面后安装或卸载 | [settings-system-043.json](../evidence/settings-system-043.json) |
| `settings.system.row_register_update` | 系统设置行更新时注册事件 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc570948`，关闭页面后安装或卸载 | [settings-system-043.json](../evidence/settings-system-043.json) |
| `settings.system.row_event_code` | 系统设置行事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc5713f0`，关闭页面后安装或卸载 | [settings-system-043.json](../evidence/settings-system-043.json) |
| `settings.system.row_index` | 系统设置行索引 | `word1` | `lv_event_get_user_data` | 调用点 `0xc5713f8`，关闭页面后安装或卸载 | [settings-system-043.json](../evidence/settings-system-043.json) |
| `settings.bluetooth.ui_create` | 蓝牙设置页面：UI 创建回调 | `word3` | `settings_bluetooth_ui_create` | 指针槽 `0x200d3300`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.bluetooth.ui_destroy` | 蓝牙设置页面：UI 销毁回调 | `void1` | `settings_bluetooth_ui_destroy` | 指针槽 `0x200d3318`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.bluetooth.headphone.ui_create` | 蓝牙耳机详情页面：UI 创建回调 | `word3` | `settings_bluetooth_headphone_ui_create` | 指针槽 `0x200d3404`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.bluetooth.headphone.ui_destroy` | 蓝牙耳机详情页面：UI 销毁回调 | `void1` | `settings_bluetooth_headphone_ui_destroy` | 指针槽 `0x200d341c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.bluetooth.off_caption` | 蓝牙关闭时提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc563e9a`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `settings.bluetooth.paired_heading` | 已配对耳机标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc562648`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `settings.bluetooth.search_caption` | 搜索状态提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc562060`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `settings.bluetooth.search_click_caption` | 开关触发搜索提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc56333a`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `settings.bluetooth.toggle_register` | 蓝牙开关事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc563da8`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `settings.bluetooth.toggle_event_code` | 蓝牙开关事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc563188`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `settings.bluetooth.headphone.name` | 耳机设备名称文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc56489c`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `settings.bluetooth.headphone.connected` | 耳机已连接文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc564a60`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `settings.bluetooth.headphone.disconnected` | 耳机未连接文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc564a2c`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `settings.bluetooth.headphone.connect_register` | 耳机连接控制事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc564bc6`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `settings.bluetooth.headphone.unpair_register` | 耳机取消配对事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc564bd4`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `settings.bluetooth.headphone.connect_event_code` | 耳机连接控制事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc564722`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `settings.bluetooth.headphone.unpair_event_code` | 耳机取消配对事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc5646b2`，关闭对应页面后安装或卸载 | [bluetooth-settings-043.json](../evidence/bluetooth-settings-043.json) |
| `apps.worldclock.main.add_event_code` | 世界时钟：主页添加按钮事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc600dea`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.main.city_event_code` | 世界时钟：主页城市行事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc600d0c`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.main.city_event_data` | 世界时钟：主页城市行事件数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc600d14`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.add_list.city_event_code` | 世界时钟：添加列表城市行事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc600a18`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.add_list.city_event_data` | 世界时钟：添加列表城市行事件数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc600a66`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.detail.delete_event_code` | 世界时钟：详情删除按钮事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc5ffae8`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.detail.delete_event_data` | 世界时钟：详情删除按钮事件数据 | `word1` | `lv_event_get_user_data` | 调用点 `0xc5ffaf0`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.main.city_register_create` | 世界时钟：主页城市行创建时事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc60144e`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.main.city_register_update` | 世界时钟：主页城市行更新时事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc6011f2`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.main.city_name_create` | 世界时钟：主页城市行创建时名称 | `void2` | `lvx_label_set_text` | 调用点 `0xc60142a`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.main.city_name_update` | 世界时钟：主页城市行更新时名称 | `void2` | `lvx_label_set_text` | 调用点 `0xc6011ce`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.main.city_time` | 世界时钟：主页城市行时间 | `void2` | `lvx_label_set_text` | 调用点 `0xc601034`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.main.city_ampm` | 世界时钟：主页城市行上午或下午 | `void2` | `lvx_label_set_text` | 调用点 `0xc60107a`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.main.city_offset` | 世界时钟：主页城市行时差 | `void2` | `lvx_label_set_text` | 调用点 `0xc600f36`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.main.city_local_time` | 世界时钟：主页城市行本地时间提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc600f7a`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.worldclock.main.limit_caption_update` | 世界时钟：主页数量上限提示更新 | `void2` | `lvx_label_set_text` | 调用点 `0xc601258`，关闭对应页面后安装或卸载 | [worldclock-actions-043.json](../evidence/worldclock-actions-043.json) |
| `apps.todolist.list.checkbox_index` | 待办事项：列表勾选事项索引 | `word1` | `lv_event_get_user_data` | 调用点 `0xc681ade`，关闭对应页面后安装或卸载 | [todolist-actions-043.json](../evidence/todolist-actions-043.json) |
| `apps.todolist.list.sub_list_index` | 待办事项：列表打开子列表的索引 | `word1` | `lv_event_get_user_data` | 调用点 `0xc6815f6`，关闭对应页面后安装或卸载 | [todolist-actions-043.json](../evidence/todolist-actions-043.json) |
| `apps.todolist.list.detail_index` | 待办事项：列表打开详情的索引 | `word1` | `lv_event_get_user_data` | 调用点 `0xc6815b2`，关闭对应页面后安装或卸载 | [todolist-actions-043.json](../evidence/todolist-actions-043.json) |
| `apps.todolist.sub_list.toggle_index` | 待办事项：子列表勾选事项索引 | `word1` | `lv_event_get_user_data` | 调用点 `0xc683268`，关闭对应页面后安装或卸载 | [todolist-actions-043.json](../evidence/todolist-actions-043.json) |
| `apps.todolist.list.row_title` | 待办事项：列表行事项标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc681644`，关闭对应页面后安装或卸载 | [todolist-actions-043.json](../evidence/todolist-actions-043.json) |
| `apps.todolist.list.row_progress` | 待办事项：列表行完成进度 | `void2` | `lvx_label_set_text` | 调用点 `0xc681742`，关闭对应页面后安装或卸载 | [todolist-actions-043.json](../evidence/todolist-actions-043.json) |
| `apps.todolist.list.row_repeat` | 待办事项：列表行重复周期 | `void2` | `lvx_label_set_text` | 调用点 `0xc681820`，关闭对应页面后安装或卸载 | [todolist-actions-043.json](../evidence/todolist-actions-043.json) |
| `apps.todolist.list.row_time_plain` | 待办事项：列表行时间文本 | `void2` | `lvx_label_set_text` | 调用点 `0xc681db6`，关闭对应页面后安装或卸载 | [todolist-actions-043.json](../evidence/todolist-actions-043.json) |
| `apps.todolist.list.row_time_alternate` | 待办事项：列表行时间文本另一分支 | `void2` | `lvx_label_set_text` | 调用点 `0xc681e30`，关闭对应页面后安装或卸载 | [todolist-actions-043.json](../evidence/todolist-actions-043.json) |
| `apps.todolist.list.row_mask_overdue` | 待办事项：列表行超时遮罩 | `void2` | `lv_image_set_src` | 调用点 `0xc681efe`，关闭对应页面后安装或卸载 | [todolist-actions-043.json](../evidence/todolist-actions-043.json) |
| `apps.todolist.list.row_mask_current` | 待办事项：列表行有效遮罩 | `void2` | `lv_image_set_src` | 调用点 `0xc681f78`，关闭对应页面后安装或卸载 | [todolist-actions-043.json](../evidence/todolist-actions-043.json) |
| `apps.perpetual.main.ui_create` | 万年历主页：UI 创建回调 | `void3` | `apps_perpetual_main_ui_create` | 指针槽 `0x200cf9d8`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.perpetual.main.ui_destroy` | 万年历主页：UI 销毁回调 | `void1` | `apps_perpetual_main_ui_destroy` | 指针槽 `0x200cf9f0`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.perpetual.day_detail.ui_create` | 万年历日期详情：UI 创建回调 | `word3` | `apps_perpetual_day_detail_ui_create` | 指针槽 `0x200cf794`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.perpetual.day_detail.ui_destroy` | 万年历日期详情：UI 销毁回调 | `void1` | `apps_perpetual_day_detail_ui_destroy` | 指针槽 `0x200cf7ac`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.perpetual.show.ui_create` | 万年历展示页：UI 创建回调 | `word3` | `apps_perpetual_show_ui_create` | 指针槽 `0x200cfa4c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.perpetual.show.ui_destroy` | 万年历展示页：UI 销毁回调 | `void1` | `apps_perpetual_show_ui_destroy` | 指针槽 `0x200cfa64`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.perpetual.schedule.ui_create` | 万年历日程详情：UI 创建回调 | `word3` | `apps_perpetual_schedule_ui_create` | 指针槽 `0x200cfac0`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.perpetual.schedule.ui_destroy` | 万年历日程详情：UI 销毁回调 | `void1` | `apps_perpetual_schedule_ui_destroy` | 指针槽 `0x200cfad8`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.perpetual.week.ui_create` | 万年历周视图：UI 创建回调 | `word3` | `apps_perpetual_week_ui_create` | 指针槽 `0x200cfb34`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.perpetual.week.ui_destroy` | 万年历周视图：UI 销毁回调 | `void1` | `apps_perpetual_week_ui_destroy` | 指针槽 `0x200cfb4c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.perpetual.main.today_text` | 主页今天按钮文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4f366a`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.main.month_text` | 主页月份文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4f3250`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.main.today_register` | 主页今天按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4f36b0`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.main.previous_register` | 主页上一月按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4f32a8`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.main.next_register` | 主页下一月按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4f32f6`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.main.scroll_start_register` | 主页滚动开始注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4f3494`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.main.scroll_end_register` | 主页滚动结束注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4f34a2`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.main.today_event_code` | 主页今天事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc4f289e`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.main.previous_event_code` | 主页上一月事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc4f3054`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.main.next_event_code` | 主页下一月事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc4f2808`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.day_detail.scroll_register` | 日期详情滚动事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4f11cc`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.schedule.title` | 日程详情标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc4f682c`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.schedule.empty_title` | 日程详情无标题提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc4f6aea`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.schedule.location_icon` | 日程详情地点图标 | `void2` | `lv_image_set_src` | 调用点 `0xc4f68b0`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.schedule.location_full` | 日程详情地点文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4f6b22`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.schedule.location_short` | 日程详情地点截断文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4f6952`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.schedule.description_icon` | 日程详情描述图标 | `void2` | `lv_image_set_src` | 调用点 `0xc4f699a`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.schedule.description_full` | 日程详情描述文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4f6b18`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.schedule.description_short` | 日程详情描述截断文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4f6a52`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.week.today_text` | 周视图今天按钮文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc4f9844`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.week.today_register` | 周视图今天按钮注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc4f9896`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `apps.perpetual.week.today_event_code` | 周视图今天事件码 | `word1` | `lv_event_get_code` | 调用点 `0xc4f9a36`，关闭对应页面后安装或卸载 | [perpetual-calendar-043.json](../evidence/perpetual-calendar-043.json) |
| `settings.notify.ui_create` | 通知设置页面：UI 创建回调 | `word3` | `settings_notify_ui_create` | 指针槽 `0x200d3824`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.notify.ui_destroy` | 通知设置页面：UI 销毁回调 | `void1` | `settings_notify_ui_destroy` | 指针槽 `0x200d383c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.notify.red_dot_register` | 红点提醒开关注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc567c08`，关闭页面后安装或卸载 | [notify-settings-043.json](../evidence/notify-settings-043.json) |
| `settings.notify.screen_register` | 通知亮屏开关注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc567d68`，关闭页面后安装或卸载 | [notify-settings-043.json](../evidence/notify-settings-043.json) |
| `settings.notify.wrist_register` | 抬腕通知开关注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc567e18`，关闭页面后安装或卸载 | [notify-settings-043.json](../evidence/notify-settings-043.json) |
| `settings.notify.wear_register` | 佩戴通知开关注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc567f80`，关闭页面后安装或卸载 | [notify-settings-043.json](../evidence/notify-settings-043.json) |
| `settings.notify.red_dot_info` | 红点提醒说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc567c7e`，关闭页面后安装或卸载 | [notify-settings-043.json](../evidence/notify-settings-043.json) |
| `settings.notify.wrist_info` | 抬腕通知说明 | `void2` | `lvx_label_set_text` | 调用点 `0xc567efe`，关闭页面后安装或卸载 | [notify-settings-043.json](../evidence/notify-settings-043.json) |
| `apps.mijia.main.ui_create` | 米家主页：UI 创建回调 | `word3` | `apps_mijia_main_ui_create` | 指针槽 `0x200d055c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.mijia.main.ui_destroy` | 米家主页：UI 销毁回调 | `void1` | `apps_mijia_main_ui_destroy` | 指针槽 `0x200d0574`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `apps.mijia.main.bt_icon` | 米家主页：蓝牙断开图标 | `void2` | `lv_image_set_src` | 调用点 `0xc507ada`，关闭页面后安装或卸载 | [mijia-main-043.json](../evidence/mijia-main-043.json) |
| `apps.mijia.main.bt_message` | 米家主页：蓝牙断开提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc507b40`，关闭页面后安装或卸载 | [mijia-main-043.json](../evidence/mijia-main-043.json) |
| `apps.mijia.main.bt_retry` | 米家主页：蓝牙断开后重连提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc507ba2`，关闭页面后安装或卸载 | [mijia-main-043.json](../evidence/mijia-main-043.json) |
| `apps.mijia.main.bt_confirm_register` | 米家主页：蓝牙断开按钮事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc50629e`，关闭页面后安装或卸载 | [mijia-main-043.json](../evidence/mijia-main-043.json) |
| `apps.mijia.main.app_icon` | 米家主页：App 断开图标 | `void2` | `lv_image_set_src` | 调用点 `0xc507cc6`，关闭页面后安装或卸载 | [mijia-main-043.json](../evidence/mijia-main-043.json) |
| `apps.mijia.main.app_message` | 米家主页：App 断开提示 | `void2` | `lvx_label_set_text` | 调用点 `0xc507cf4`，关闭页面后安装或卸载 | [mijia-main-043.json](../evidence/mijia-main-043.json) |
| `apps.mijia.main.app_confirm_register` | 米家主页：App 断开按钮事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc50627e`，关闭页面后安装或卸载 | [mijia-main-043.json](../evidence/mijia-main-043.json) |
| `apps.mijia.main.family_heading` | 米家主页：多个家庭时标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc5065cc`，关闭页面后安装或卸载 | [mijia-main-043.json](../evidence/mijia-main-043.json) |
| `settings.down_key.ui_create` | 下按键设置：UI 创建回调 | `word3` | `settings_down_key_ui_create` | 指针槽 `0x200d2fe4`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.down_key.ui_destroy` | 下按键设置：UI 销毁回调 | `void1` | `settings_down_key_ui_destroy` | 指针槽 `0x200d2ffc`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.quick_gesture.ui_create` | 快捷手势设置：UI 创建回调 | `word3` | `settings_quick_gesture_ui_create` | 指针槽 `0x200d3124`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.quick_gesture.ui_destroy` | 快捷手势设置：UI 销毁回调 | `void1` | `settings_quick_gesture_ui_destroy` | 指针槽 `0x200d313c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.gesture_guide.ui_create` | 快捷手势说明：UI 创建回调 | `word3` | `settings_gesture_guide_ui_create` | 指针槽 `0x200d3198`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.gesture_guide.ui_destroy` | 快捷手势说明：UI 销毁回调 | `void1` | `settings_gesture_guide_ui_destroy` | 指针槽 `0x200d31b0`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.gesture_guide.step1` | 手势说明第 1 段 | `void2` | `lvx_label_set_text` | 调用点 `0xc55f93e`，关闭对应页面后安装或卸载 | [input-settings-043.json](../evidence/input-settings-043.json) |
| `settings.gesture_guide.step2` | 手势说明第 2 段 | `void2` | `lvx_label_set_text` | 调用点 `0xc55f99e`，关闭对应页面后安装或卸载 | [input-settings-043.json](../evidence/input-settings-043.json) |
| `settings.gesture_guide.step3` | 手势说明第 3 段 | `void2` | `lvx_label_set_text` | 调用点 `0xc55f9fa`，关闭对应页面后安装或卸载 | [input-settings-043.json](../evidence/input-settings-043.json) |
| `settings.gesture_guide.step4` | 手势说明第 4 段 | `void2` | `lvx_label_set_text` | 调用点 `0xc55fa56`，关闭对应页面后安装或卸载 | [input-settings-043.json](../evidence/input-settings-043.json) |
| `settings.gesture_guide.step5` | 手势说明第 5 段 | `void2` | `lvx_label_set_text` | 调用点 `0xc55fab0`，关闭对应页面后安装或卸载 | [input-settings-043.json](../evidence/input-settings-043.json) |
| `settings.down_key.selected_index` | 下按键设置：点击选项时读取索引 | `word1` | `lv_event_get_user_data` | 调用点 `0xc55dc44`，关闭页面后安装或卸载 | [down-key-actions-043.json](../evidence/down-key-actions-043.json) |
| `settings.down_key.register_create` | 下按键设置：创建选项时注册点击回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc55df9a`，关闭页面后安装或卸载 | [down-key-actions-043.json](../evidence/down-key-actions-043.json) |
| `settings.down_key.register_update` | 下按键设置：更新选项时注册点击回调 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc55dd32`，关闭页面后安装或卸载 | [down-key-actions-043.json](../evidence/down-key-actions-043.json) |
| `settings.quick_gesture.off_switch_register` | 快捷手势：关闭态开关注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc55e524`，关闭页面后安装或卸载 | [quick-gesture-actions-043.json](../evidence/quick-gesture-actions-043.json) |
| `settings.quick_gesture.off_guide_register` | 快捷手势：关闭态说明入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc55e624`，关闭页面后安装或卸载 | [quick-gesture-actions-043.json](../evidence/quick-gesture-actions-043.json) |
| `settings.quick_gesture.on_switch_register` | 快捷手势：开启态开关注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc55ea5c`，关闭页面后安装或卸载 | [quick-gesture-actions-043.json](../evidence/quick-gesture-actions-043.json) |
| `settings.quick_gesture.on_option2_register` | 快捷手势：开启态选项 2 注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc55ec74`，关闭页面后安装或卸载 | [quick-gesture-actions-043.json](../evidence/quick-gesture-actions-043.json) |
| `settings.quick_gesture.on_option3_register` | 快捷手势：开启态选项 3 注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc55ed22`，关闭页面后安装或卸载 | [quick-gesture-actions-043.json](../evidence/quick-gesture-actions-043.json) |
| `settings.quick_gesture.on_option6_register` | 快捷手势：开启态选项 6 注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc55ed90`，关闭页面后安装或卸载 | [quick-gesture-actions-043.json](../evidence/quick-gesture-actions-043.json) |
| `settings.quick_gesture.on_guide_register` | 快捷手势：开启态说明入口注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc55ee12`，关闭页面后安装或卸载 | [quick-gesture-actions-043.json](../evidence/quick-gesture-actions-043.json) |
| `settings.quick_gesture.off_description` | 快捷手势：关闭态说明文字 | `void2` | `lvx_label_set_text` | 调用点 `0xc55e58e`，关闭页面后安装或卸载 | [quick-gesture-actions-043.json](../evidence/quick-gesture-actions-043.json) |
| `settings.quick_gesture.on_heading` | 快捷手势：开启态设置说明标题 | `void2` | `lvx_label_set_text` | 调用点 `0xc55ead2`，关闭页面后安装或卸载 | [quick-gesture-actions-043.json](../evidence/quick-gesture-actions-043.json) |
| `settings.gesture_action.ui_create` | 手势功能设置：UI 创建回调 | `word3` | `settings_gesture_action_ui_create` | 指针槽 `0x200d320c`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.gesture_action.ui_destroy` | 手势功能设置：UI 销毁回调 | `void1` | `settings_gesture_action_ui_destroy` | 指针槽 `0x200d3224`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.gesture_teach.ui_create` | 手势教学选择：UI 创建回调 | `word3` | `settings_gesture_teach_ui_create` | 指针槽 `0x200d3288`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.gesture_teach.ui_destroy` | 手势教学选择：UI 销毁回调 | `void1` | `settings_gesture_teach_ui_destroy` | 指针槽 `0x200d32a0`，关闭页面后安装或卸载 | [page-lifecycle-043.json](../evidence/page-lifecycle-043.json) |
| `settings.gesture_action.selected_index` | 手势功能选择索引 | `word1` | `lv_event_get_user_data` | 调用点 `0xc56021e`，关闭对应页面后安装或卸载 | [gesture-subsettings-043.json](../evidence/gesture-subsettings-043.json) |
| `settings.gesture_action.first_register` | 功能列表首项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc560a50`，关闭对应页面后安装或卸载 | [gesture-subsettings-043.json](../evidence/gesture-subsettings-043.json) |
| `settings.gesture_action.camera_register` | 相机功能选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc560b8a`，关闭对应页面后安装或卸载 | [gesture-subsettings-043.json](../evidence/gesture-subsettings-043.json) |
| `settings.gesture_action.other_register` | 功能列表其他项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc560cde`，关闭对应页面后安装或卸载 | [gesture-subsettings-043.json](../evidence/gesture-subsettings-043.json) |
| `settings.gesture_action.training_register` | 训练开始事件注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc5600b0`，关闭对应页面后安装或卸载 | [gesture-subsettings-043.json](../evidence/gesture-subsettings-043.json) |
| `settings.gesture_teach.roll_register` | 教学翻腕选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc56133e`，关闭对应页面后安装或卸载 | [gesture-subsettings-043.json](../evidence/gesture-subsettings-043.json) |
| `settings.gesture_teach.shake_register` | 教学摇腕选项注册 | `word4` | `lv_obj_add_event_cb` | 调用点 `0xc561380`，关闭对应页面后安装或卸载 | [gesture-subsettings-043.json](../evidence/gesture-subsettings-043.json) |
| `ui.image.create` | LVGL 图像对象创建；涉及所有调用者 | `word2` | `lv_image_create` | 全局入口；安装、卸载前需确保受影响线程静止 | [os-version-043.json](../evidence/os-version-043.json) |
| `ui.image.set_angle` | LVGL 图像旋转角设置；涉及所有调用者 | `void2` | `lv_image_set_angle` | 全局入口；参数 1 为十分之一度，安装、卸载前需确保受影响线程静止 | [compass-rotation-043.json](../evidence/compass-rotation-043.json) |
| `ui.image.set_source` | LVGL 图像资源设置；涉及所有调用者 | `void2` | `lv_image_set_src` | 全局入口；安装、卸载前需确保受影响线程静止 | [image-source-043.json](../evidence/image-source-043.json) |
| `ui.event.user_data` | LVGL 事件用户数据读取；涉及所有调用者 | `word1` | `lv_event_get_user_data` | 全局入口；安装、卸载前需确保受影响线程静止 | [return-to-dial-option-043.json](../evidence/return-to-dial-option-043.json) |
| `ui.event.code` | LVGL 事件代码读取；涉及所有调用者 | `word1` | `lv_event_get_code` | 全局入口；安装、卸载前需确保受影响线程静止 | [event-code-043.json](../evidence/event-code-043.json) |
| `ui.event.current_target` | 当前正在处理事件的对象读取；涉及所有调用者 | `word1` | `lv_event_current_target` | 全局入口；安装、卸载前需确保受影响线程静止 | [event-targets-043.json](../evidence/event-targets-043.json) |
| `ui.event.original_target` | 事件初始目标对象读取；涉及所有调用者 | `word1` | `lv_event_original_target` | 全局入口；安装、卸载前需确保受影响线程静止 | [event-targets-043.json](../evidence/event-targets-043.json) |
| `ui.event.parameter` | 事件参数指针读取；涉及所有调用者 | `word1` | `lv_event_parameter` | 全局入口；安装、卸载前需确保受影响线程静止 | [event-targets-043.json](../evidence/event-targets-043.json) |
| `ui.label.set_text` | 标签文字设置；涉及所有调用者 | `void2` | `lvx_label_set_text` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-object-global-043.json](../evidence/ui-object-global-043.json) |
| `ui.object.set_size` | 控件宽高设置；涉及所有调用者 | `void3` | `lv_obj_set_size` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-object-global-043.json](../evidence/ui-object-global-043.json) |
| `ui.object.add_flag` | 添加控件标志；涉及所有调用者 | `void2` | `lv_obj_add_flag` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-object-global-043.json](../evidence/ui-object-global-043.json) |
| `ui.object.clear_flag` | 清除控件标志；涉及所有调用者 | `void2` | `lv_obj_clear_flag` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-object-state-043.json](../evidence/ui-object-state-043.json) |
| `ui.object.has_flag` | 查询控件是否包含全部指定标志；涉及所有调用者 | `word2` | `lv_obj_has_flag` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-object-state-043.json](../evidence/ui-object-state-043.json) |
| `ui.object.has_state` | 查询控件是否包含任一指定状态；涉及所有调用者 | `word2` | `lv_obj_has_state` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-object-state-043.json](../evidence/ui-object-state-043.json) |
| `ui.object.clean` | 清除对象的子控件；涉及所有调用者 | `void1` | `lv_obj_clean` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-object-clean-043.json](../evidence/ui-object-clean-043.json) |
| `ui.object.create` | 创建基础控件；涉及所有经过此入口的调用者 | `word2` | `lv_obj_create` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-object-create-043.json](../evidence/ui-object-create-043.json) |
| `ui.object.delete` | 删除控件对象；涉及所有经过此入口的调用者 | `void1` | `lv_obj_delete` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-object-delete-043.json](../evidence/ui-object-delete-043.json) |
| `ui.object.class_allocate` | 按类分配控件并关联父对象，类初始化发生在之后 | `word2` | `lv_obj_class_create_obj` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-object-class-events-043.json](../evidence/ui-object-class-events-043.json) |
| `ui.object.event_add` | 向控件注册事件回调 | `word4` | `lv_obj_add_event_cb` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-object-class-events-043.json](../evidence/ui-object-class-events-043.json) |
| `ui.object.event_remove` | 按回调函数移除一个控件事件回调 | `word2` | `lv_obj_remove_event_cb` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-object-class-events-043.json](../evidence/ui-object-class-events-043.json) |
| `ui.object.send_event` | 向对象发送事件并执行相应回调和类处理 | `word3` | `lv_obj_send_event` | 全局入口；安装、卸载前需确保受影响线程静止 | [ui-event-send-043.json](../evidence/ui-event-send-043.json) |
| `system.navigation.page` | 系统页面导航，通过共享函数表发起页面切换 | `word1` | `navigator_page` | 指针槽 `0x200eb6e4`，仅覆盖经此槽的调用 | [system-navigation-043.json](../evidence/system-navigation-043.json) |
| `system.navigation.app` | 系统应用导航，通过共享函数表发起应用切换 | `word1` | `navigator_app` | 指针槽 `0x200eb6e8`，仅覆盖经此槽的调用 | [system-navigation-043.json](../evidence/system-navigation-043.json) |
| `system.navigation.back` | 系统返回导航，通过共享函数表发起返回 | `word1` | `navigator_back` | 指针槽 `0x200eb6ec`，仅覆盖经此槽的调用 | [system-navigation-043.json](../evidence/system-navigation-043.json) |
| `system.navigation.finish_page` | 结束指定页面或当前栈顶页面 | `word1` | `navigator_finish` | 指针槽 `0x200eb6e0`，仅覆盖经此槽的调用 | [system-navigation-043.json](../evidence/system-navigation-043.json) |
| `system.navigation.home` | 返回主界面，可选择转场模式 | `word1` | `navigator_home` | 指针槽 `0x200eb6f0`，仅覆盖经此槽的调用 | [system-navigation-043.json](../evidence/system-navigation-043.json) |
| `system.navigation.background_page` | 通过后台页面导航路径切换页面 | `word1` | `navigator_background` | 指针槽 `0x200eb6f4`，仅覆盖经此槽的调用 | [system-navigation-043.json](../evidence/system-navigation-043.json) |
| `system.apps.kill_background` | 请求终止后台应用 | `word2` | `apps_kill_background` | 指针槽 `0x200eb6f8`，仅覆盖经此槽的调用 | [system-navigation-043.json](../evidence/system-navigation-043.json) |
| `system.apps.kill` | 请求终止指定包名的应用 | `word3` | `apps_kill` | 指针槽 `0x200eb6fc`，仅覆盖经此槽的调用 | [system-navigation-043.json](../evidence/system-navigation-043.json) |

| 原生目标 | Thumb 可调用地址 | 16 字节预期签名 | 参数 / 返回 |
| --- | --- | --- | --- |
| `lvx_label_set_text` | `0x1c06f039` | `2de9f0410d4600af0446bcf75ff9b5b3` | `void(label, const char *text)` |
| `lv_image_create` | `0x1c06cac1` | `98b503460c4600af19460448bcf758fa` | `void *(parent, const uint8_t *options)` |
| `lv_image_set_src` | `0x1c06ceb5` | `2de9f0430d468fb004af0446bef720fa` | `void(image, const void *source)` |
| `lv_obj_add_flag` | `0x1c028bd9` | `2de9f04188b00d4600af044601f04efc` | `void(object, uint32_t flags)` |
| `lv_obj_set_size` | `0x1c02a2d1` | `f0b5144683b000af0e46002301213a1d` | `void(object, int32_t width, int32_t height)` |
| `lv_event_get_user_data` | `0x002bfd89` | `80b4c06800afbd465df8047b704700bf` | `void *(event)` |
| `lv_event_get_code` | `0x002bfd65` | `80b4008900afc0f30e00bd465df8047b` | `uint32_t(event)` |
| `lv_event_current_target` | `0x002bfd45` | `80b4006800afbd465df8047b704700bf` | `void *(event)` |
| `lv_event_original_target` | `0x002bfd55` | `80b4406800afbd465df8047b704700bf` | `void *(event)` |
| `lv_event_parameter` | `0x002bfd79` | `80b4006900afbd465df8047b704700bf` | `void *(event)` |
| `lv_obj_clear_flag` | `0x1c028c85` | `f0b589b00d4600af044601f0f9fbea06` | `void(object, uint32_t flags)` |
| `lv_obj_has_flag` | `0x1c028d95` | `80b4c36a00af99430cbf01200020bd46` | `uint32_t(object, uint32_t flags)` |
| `lv_obj_has_state` | `0x1c028dd5` | `80b4038e00af194214bf01200020bd46` | `uint32_t(object, uint32_t states)` |
| `lv_obj_clean` | `0x1c02ecf1` | `f8b5054600affcf705fbaa68002a60d0` | `void(object)` |
| `lv_obj_create` | `0x1c028bb5` | `0246b0b506480d4600af114600f0def9` | `void *(parent, const uint8_t *options)` |
| `lv_obj_delete` | `0x1c02ecdd` | `90f83330db0600d5704780b500affff7` | `void(object)` |
| `lv_obj_class_create_obj` | `0x1c028f81` | `f0b583b006460d4602af50b10346354c` | `void *(class, parent)` |
| `lv_obj_add_event_cb` | `0x002bf7ad` | `2de9f04180460c4615461e4600af03f0` | `void *(object, callback, filter, user_data)` |
| `lv_obj_remove_event_cb` | `0x002bf811` | `2de9f0410546806800afa0b10c308846` | `uint32_t(object, callback)` |
| `lv_obj_send_event` | `0x002bf691` | `b0b588b000af38b300243b7ec7e90000` | `uint32_t(object, uint16_t code, void *parameter)` |

| 指针目标 | RAM 槽地址 | 启动时的原函数指针 | 参数 / 返回 |
| --- | --- | --- | --- |
| `navigator_page` | `0x200eb6e4` | `0x0ca6d2f9` | `uint32_t(navigation_action *)` |
| `navigator_app` | `0x200eb6e8` | `0x0ca6d4b5` | `uint32_t(navigation_action *)` |
| `navigator_back` | `0x200eb6ec` | `0x0ca6d695` | `uint32_t(navigation_action *)` |
| `navigator_finish` | `0x200eb6e0` | `0x0ca6d2d1` | `uint32_t(navigation_action *)` |
| `navigator_home` | `0x200eb6f0` | `0x0ca6d2c5` | `uint32_t(uint32_t mode)` |
| `navigator_background` | `0x200eb6f4` | `0x0ca6d595` | `uint32_t(navigation_action *)` |
| `apps_kill_background` | `0x200eb6f8` | `0x0ca6d2b9` | `uint32_t(const char *requester, uint32_t reason)` |
| `apps_kill` | `0x200eb6fc` | `0x0ca6d2ad` | `uint32_t(const char *requester, uint32_t reason, const char *package)` |
| `settings_about_ui_create` | `0x200d207c` | `0xc54d635` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_about_ui_destroy` | `0x200d2094` | `0xc54d551` | `void(void *page)` |
| `settings_display_brightness_ui_create` | `0x200d2898` | `0xc5555ad` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_display_brightness_ui_destroy` | `0x200d28b0` | `0xc554ea1` | `void(void *page)` |
| `settings_dnd_ui_create` | `0x200d2b68` | `0xc559ca9` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_dnd_ui_destroy` | `0x200d2b80` | `0xc559705` | `void(void *page)` |
| `settings_battery_ui_create` | `0x200d2338` | `0xc54f679` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_battery_ui_destroy` | `0x200d2350` | `0xc54e465` | `void(void *page)` |
| `settings_connectivity_ui_create` | `0x200d2518` | `0xc5511e5` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_connectivity_ui_destroy` | `0x200d2530` | `0xc551161` | `void(void *page)` |
| `health_heart_rate_ui_create` | `0x200dbecc` | `0xc664ffd` | `uintptr_t(void *page, void *root, void *data)` |
| `health_heart_rate_ui_destroy` | `0x200dbee4` | `0xc664c65` | `void(void *page)` |
| `watchface_dual_time_ui_create` | `0x200d8cac` | `0xc5f1f21` | `uintptr_t(void *page, void *root, void *data)` |
| `watchface_dual_time_ui_destroy` | `0x200d8cc4` | `0xc5f1ef1` | `void(void *page)` |
| `apps_mijia_scene_ui_create` | `0x200d05d0` | `0xc5077b1` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_mijia_scene_ui_destroy` | `0x200d05e8` | `0xc5076b1` | `void(void *page)` |
| `apps_timer_ui_create` | `0x200d0308` | `0xc4ffab1` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_timer_ui_destroy` | `0x200d0320` | `0xc4ff515` | `void(void *page)` |
| `apps_alarm_ui_create` | `0x200d14e4` | `0xc53d711` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_alarm_ui_destroy` | `0x200d14fc` | `0xc53d375` | `void(void *page)` |
| `apps_weather_ui_create` | `0x200da430` | `0xc60fa01` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_weather_ui_destroy` | `0x200da448` | `0xc60f139` | `void(void *page)` |
| `health_sleep_ui_create` | `0x200db1c4` | `0xc63e345` | `uintptr_t(void *page, void *root, void *data)` |
| `health_sleep_ui_destroy` | `0x200db1dc` | `0xc63de59` | `void(void *page)` |
| `health_oxygen_ui_create` | `0x200db520` | `0xc64be19` | `void(void *page, void *root, void *data)` |
| `health_oxygen_ui_destroy` | `0x200db538` | `0xc64aca1` | `void(void *page)` |
| `system_launcher_ui_create` | `0x200d0d58` | `0xc517c81` | `uintptr_t(void *page, void *root, void *data)` |
| `system_launcher_ui_destroy` | `0x200d0d70` | `0xc51755d` | `void(void *page)` |
| `sports_list_ui_create` | `0x200d5070` | `0xc58fb4d` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_list_ui_destroy` | `0x200d5088` | `0xc58fb05` | `void(void *page)` |
| `health_stress_ui_create` | `0x200dae14` | `0xc63107d` | `uintptr_t(void *page, void *root, void *data)` |
| `health_stress_ui_destroy` | `0x200dae2c` | `0xc62fec5` | `void(void *page)` |
| `health_breath_ui_create` | `0x200dac60` | `0xc629f31` | `uintptr_t(void *page, void *root, void *data)` |
| `health_breath_ui_destroy` | `0x200dac78` | `0xc629ead` | `void(void *page)` |
| `health_heart_rate_settings_ui_create` | `0x200dc03c` | `0xc6681f5` | `uintptr_t(void *page, void *root, void *data)` |
| `health_heart_rate_settings_ui_destroy` | `0x200dc054` | `0xc667e91` | `void(void *page)` |
| `health_stress_settings_ui_create` | `0x200daf70` | `0xc6336c1` | `uintptr_t(void *page, void *root, void *data)` |
| `health_stress_settings_ui_destroy` | `0x200daf88` | `0xc633485` | `void(void *page)` |
| `health_sleep_settings_ui_create` | `0x200db350` | `0xc640ef9` | `uintptr_t(void *page, void *root, void *data)` |
| `health_sleep_settings_ui_destroy` | `0x200db368` | `0xc640e09` | `void(void *page)` |
| `health_oxygen_settings_ui_create` | `0x200db608` | `0xc64d745` | `uintptr_t(void *page, void *root, void *data)` |
| `health_oxygen_settings_ui_destroy` | `0x200db620` | `0xc64d459` | `void(void *page)` |
| `health_breath_session_ui_create` | `0x200dacd4` | `0xc62b819` | `uintptr_t(void *page, void *root, void *data)` |
| `health_breath_session_ui_destroy` | `0x200dacec` | `0xc62b305` | `void(void *page)` |
| `apps_compass_ui_create` | `0x200d0250` | `0xc4fe531` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_compass_ui_destroy` | `0x200d0268` | `0xc4fd6c1` | `void(void *page)` |
| `apps_flashlight_ui_create` | `0x200d07bc` | `0xc509005` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_flashlight_ui_destroy` | `0x200d07d4` | `0xc508711` | `void(void *page)` |
| `apps_calendar_ui_create` | `0x200cf668` | `0xc4e9705` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_calendar_ui_destroy` | `0x200cf680` | `0xc4e6c4d` | `void(void *page)` |
| `apps_stopwatch_ui_create` | `0x200d0164` | `0xc4fa1c1` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_stopwatch_ui_destroy` | `0x200d017c` | `0xc4fb045` | `void(void *page)` |
| `system_notifications_detail_ui_create` | `0x200d1180` | `0xc52613d` | `uintptr_t(void *page, void *root, void *data)` |
| `system_notifications_detail_ui_destroy` | `0x200d1198` | `0xc5260a9` | `void(void *page)` |
| `system_notifications_aggregation_ui_create` | `0x200d110c` | `0xc525afd` | `uintptr_t(void *page, void *root, void *data)` |
| `system_notifications_aggregation_ui_destroy` | `0x200d1124` | `0xc525b19` | `void(void *page)` |

| `health_activity_ui_create` | `0x200cf098` | `0xc4d1e2d` | `uintptr_t(void *page, void *root, void *data)` |
| `health_activity_ui_destroy` | `0x200cf0b0` | `0xc4d1db5` | `void(void *page)` |
| `apps_media_ui_create` | `0x200d0f6c` | `0xc51b1e1` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_media_ui_destroy` | `0x200d0f84` | `0xc51b385` | `void(void *page)` |
| `apps_recorder_ui_create` | `0x200da5d8` | `0xc61a88d` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_recorder_ui_destroy` | `0x200da5f0` | `0xc618d25` | `void(void *page)` |
| `health_vitality_ui_create` | `0x200db79c` | `0xc650901` | `uintptr_t(void *page, void *root, void *data)` |
| `health_vitality_ui_destroy` | `0x200db7b4` | `0xc64fca5` | `void(void *page)` |
| `health_women_ui_create` | `0x200da7ec` | `0xc621945` | `uintptr_t(void *page, void *root, void *data)` |
| `health_women_ui_destroy` | `0x200da804` | `0xc6211bd` | `void(void *page)` |

| `settings_sound_ui_create` | `0x200d3d68` | `0xc56f819` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_sound_ui_destroy` | `0x200d3d80` | `0xc56fc81` | `void(void *page)` |
| `settings_vibration_ui_create` | `0x200d3ddc` | `0xc56ff6d` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_vibration_ui_destroy` | `0x200d3df4` | `0xc56fcc5` | `void(void *page)` |

| `settings_notification_center_ui_create` | `0x200d3898` | `0xc56863d` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_notification_center_ui_destroy` | `0x200d38b0` | `0xc5682a9` | `void(void *page)` |
| `settings_control_center_ui_create` | `0x200d262c` | `0xc55183d` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_control_center_ui_destroy` | `0x200d2644` | `0xc5517e5` | `void(void *page)` |

| `health_activity_explain_ui_create` | `0x200ceff4` | `0xc4d10a5` | `uintptr_t(void *page, void *root, void *data)` |
| `health_activity_explain_ui_destroy` | `0x200cf00c` | `0xc4d0f45` | `void(void *page)` |

| `apps_calendar_detail_ui_create` | `0x200cf5f4` | `0xc4e6be5` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_calendar_detail_ui_destroy` | `0x200cf60c` | `0xc4e6071` | `void(void *page)` |
| `apps_weather_forecast_ui_create` | `0x200da3bc` | `0xc60eb0d` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_weather_forecast_ui_destroy` | `0x200da3d4` | `0xc60ead9` | `void(void *page)` |
| `apps_weather_reminder_ui_create` | `0x200da4a4` | `0xc60fca9` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_weather_reminder_ui_destroy` | `0x200da4bc` | `0xc60fbd9` | `void(void *page)` |

| `apps_weather_detail_ui_create` | `0x200da340` | `0xc60aa2d` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_weather_detail_ui_destroy` | `0x200da358` | `0xc609f19` | `void(void *page)` |

| `lv_image_set_angle` | `0x1c06caf9` | `2de9f0418ab090f86130054603f00f03` | `void(image, int32_t angle_tenths)` |

| `health_oxygen_threshold_ui_create` | `0x200db67c` | `0xc64dd11` | `uintptr_t(void *page, void *root, void *data)` |
| `health_oxygen_threshold_ui_destroy` | `0x200db694` | `0xc64d99d` | `void(void *page)` |

| `health_sleep_settings_list_ui_create` | `0x200db3c4` | `0xc641775` | `uintptr_t(void *page, void *root, void *data)` |
| `health_sleep_settings_list_ui_destroy` | `0x200db3dc` | `0xc641529` | `void(void *page)` |
| `health_sleep_survey_ui_create` | `0x200db238` | `0xc640735` | `uintptr_t(void *page, void *root, void *data)` |
| `health_sleep_survey_ui_destroy` | `0x200db250` | `0xc6404a5` | `void(void *page)` |
| `health_sleep_survey_done_ui_create` | `0x200db2dc` | `0xc640da5` | `uintptr_t(void *page, void *root, void *data)` |
| `health_sleep_survey_done_ui_destroy` | `0x200db2f4` | `0xc640bf1` | `void(void *page)` |

| `health_oxygen_measure_ui_create` | `0x200db594` | `0xc64c46d` | `uintptr_t(void *page, void *root, void *data)` |
| `health_oxygen_measure_ui_destroy` | `0x200db5ac` | `0xc64c3a1` | `void(void *page)` |
| `health_oxygen_low_chart_ui_create` | `0x200db4ac` | `0xc64a189` | `uintptr_t(void *page, void *root, void *data)` |
| `health_oxygen_low_chart_ui_destroy` | `0x200db4c4` | `0xc649985` | `void(void *page)` |

| `health_breath_info_ui_create` | `0x200dabec` | `0xc629761` | `uintptr_t(void *page, void *root, void *data)` |
| `health_breath_info_ui_destroy` | `0x200dac04` | `0xc6295a1` | `void(void *page)` |

| `health_sleep_hrv_detail_ui_create` | `0x200db058` | `0xc63c299` | `uintptr_t(void *page, void *root, void *data)` |
| `health_sleep_hrv_detail_ui_destroy` | `0x200db070` | `0xc63c151` | `void(void *page)` |
| `health_sleep_hrv_explain_ui_create` | `0x200db0cc` | `0xc63d721` | `uintptr_t(void *page, void *root, void *data)` |
| `health_sleep_hrv_explain_ui_destroy` | `0x200db0e4` | `0xc63d319` | `void(void *page)` |
| `health_sleep_hrv_info_ui_create` | `0x200db140` | `0xc63dd6d` | `uintptr_t(void *page, void *root, void *data)` |
| `health_sleep_hrv_info_ui_destroy` | `0x200db158` | `0xc63d791` | `void(void *page)` |
| `health_stress_measure_ui_create` | `0x200dae88` | `0xc631ddd` | `uintptr_t(void *page, void *root, void *data)` |
| `health_stress_measure_ui_destroy` | `0x200daea0` | `0xc632181` | `void(void *page)` |
| `health_stress_month_ui_create` | `0x200daefc` | `0xc63342d` | `uintptr_t(void *page, void *root, void *data)` |
| `health_stress_month_ui_destroy` | `0x200daf14` | `0xc632c25` | `void(void *page)` |

| `health_stress_explain_ui_create` | `0x200dada0` | `0xc62e2e1` | `uintptr_t(void *page, void *root, void *data)` |
| `health_stress_explain_ui_destroy` | `0x200dadb8` | `0xc62d8c5` | `void(void *page)` |
| `health_heart_rate_abnormal_ui_create` | `0x200dbde4` | `0xc662c95` | `uintptr_t(void *page, void *root, void *data)` |
| `health_heart_rate_abnormal_ui_destroy` | `0x200dbdfc` | `0xc662b39` | `void(void *page)` |
| `health_heart_rate_explain_ui_create` | `0x200dbe58` | `0xc6643f5` | `uintptr_t(void *page, void *root, void *data)` |
| `health_heart_rate_explain_ui_destroy` | `0x200dbe70` | `0xc663b49` | `void(void *page)` |
| `health_heart_rate_rest_ui_create` | `0x200dbfc8` | `0xc667a75` | `uintptr_t(void *page, void *root, void *data)` |
| `health_heart_rate_rest_ui_destroy` | `0x200dbfe0` | `0xc6679b5` | `void(void *page)` |
| `health_heart_rate_catalog_ui_create` | `0x200dc124` | `0xc668b65` | `void(void *page, void *root, void *data)` |
| `health_heart_rate_catalog_ui_destroy` | `0x200dc13c` | `0xc668471` | `void(void *page)` |

| `sports_categories_ui_create` | `0x200d4f7c` | `0xc58ee85` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_categories_ui_destroy` | `0x200d4f94` | `0xc58ee59` | `void(void *page)` |
| `sports_category_list_ui_create` | `0x200d50e4` | `0xc58fbed` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_category_list_ui_destroy` | `0x200d50fc` | `0xc58fbb1` | `void(void *page)` |
| `sports_list_edit_ui_create` | `0x200d4ff0` | `0xc58f66d` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_list_edit_ui_destroy` | `0x200d5008` | `0xc58f0d5` | `void(void *page)` |
| `sports_countdown_ui_create` | `0x200d53cc` | `0xc596c65` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_countdown_ui_destroy` | `0x200d53e4` | `0xc596ee5` | `void(void *page)` |

| `sports_settings_ui_create` | `0x200d7f98` | `0xc5be3d9` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_settings_ui_destroy` | `0x200d7fb0` | `0xc5be24d` | `void(void *page)` |
| `sports_settings_detail_ui_create` | `0x200d7ccc` | `0xc5b9b51` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_settings_detail_ui_destroy` | `0x200d7ce4` | `0xc5b9af5` | `void(void *page)` |
| `sports_settings_switch_ui_create` | `0x200d8058` | `0xc5bf0d1` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_settings_switch_ui_destroy` | `0x200d8070` | `0xc5be9e1` | `void(void *page)` |
| `sports_settings_radio_ui_create` | `0x200d7f24` | `0xc5bdf69` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_settings_radio_ui_destroy` | `0x200d7f3c` | `0xc5bdebd` | `void(void *page)` |
| `sports_settings_picker_ui_create` | `0x200d7eb0` | `0xc5bde45` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_settings_picker_ui_destroy` | `0x200d7ec8` | `0xc5bba05` | `void(void *page)` |

| `sports_waiting_ui_create` | `0x200d851c` | `0xc5ccac5` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_waiting_ui_destroy` | `0x200d8534` | `0xc5cc5e1` | `void(void *page)` |
| `sports_realtime_ui_create` | `0x200d5354` | `0xc595f25` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_realtime_ui_destroy` | `0x200d536c` | `0xc595d5d` | `void(void *page)` |
| `sports_voice_ui_create` | `0x200d559c` | `0xc5979a5` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_voice_ui_destroy` | `0x200d55b4` | `0xc597919` | `void(void *page)` |

| `sports_warmup_ui_create` | `0x200d8700` | `0xc5d1ced` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_warmup_ui_destroy` | `0x200d8718` | `0xc5d1429` | `void(void *page)` |
| `sports_warmup_explain_ui_create` | `0x200d860c` | `0xc5ce89d` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_warmup_explain_ui_destroy` | `0x200d8624` | `0xc5ce3b5` | `void(void *page)` |
| `sports_warmup_anim_ui_create` | `0x200d8680` | `0xc5cf0a5` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_warmup_anim_ui_destroy` | `0x200d8698` | `0xc5ced99` | `void(void *page)` |
| `sports_settings_ephemeris_ui_create` | `0x200d7d40` | `0xc5ba351` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_settings_ephemeris_ui_destroy` | `0x200d7d58` | `0xc5b9be5` | `void(void *page)` |
| `sports_settings_ephemeris_sub_ui_create` | `0x200d7db4` | `0xc5bae0d` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_settings_ephemeris_sub_ui_destroy` | `0x200d7dcc` | `0xc5ba545` | `void(void *page)` |
| `sports_settings_general_ui_create` | `0x200d7e28` | `0xc5bb205` | `uintptr_t(void *page, void *root, void *data)` |
| `sports_settings_general_ui_destroy` | `0x200d7e40` | `0xc5bb0d5` | `void(void *page)` |

| `apps_pomodoro_main_ui_create` | `0x200d1bd4` | `0xc5458f5` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_pomodoro_main_ui_destroy` | `0x200d1bec` | `0xc545625` | `void(void *page)` |
| `apps_pomodoro_set_ui_create` | `0x200d1cbc` | `0xc5461d5` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_pomodoro_set_ui_destroy` | `0x200d1cd4` | `0xc54609d` | `void(void *page)` |
| `apps_pomodoro_info_ui_create` | `0x200d1b60` | `0xc5452f5` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_pomodoro_info_ui_destroy` | `0x200d1b78` | `0xc5452c5` | `void(void *page)` |
| `apps_pomodoro_activity_ui_create` | `0x200d1a58` | `0xc544941` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_pomodoro_activity_ui_destroy` | `0x200d1a70` | `0xc543dc9` | `void(void *page)` |
| `apps_pomodoro_notice_ui_create` | `0x200d1c48` | `0xc545ee9` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_pomodoro_notice_ui_destroy` | `0x200d1c60` | `0xc545e81` | `void(void *page)` |
| `apps_pomodoro_end_ui_create` | `0x200d1aec` | `0xc5450f9` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_pomodoro_end_ui_destroy` | `0x200d1b04` | `0xc5450a5` | `void(void *page)` |

| `apps_alarm_custom_ui_create` | `0x200d13ac` | `0xc53c135` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_alarm_custom_ui_destroy` | `0x200d13c4` | `0xc53bf59` | `void(void *page)` |
| `apps_alarm_edit_ui_create` | `0x200d1448` | `0xc53d0e9` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_alarm_edit_ui_destroy` | `0x200d1460` | `0xc53c6f1` | `void(void *page)` |
| `apps_alarm_repeat_page_ui_create` | `0x200d1580` | `0xc53ebd9` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_alarm_repeat_page_ui_destroy` | `0x200d1598` | `0xc53e811` | `void(void *page)` |
| `apps_alarm_smart_ui_create` | `0x200d161c` | `0xc53f3f9` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_alarm_smart_ui_destroy` | `0x200d1634` | `0xc53f23d` | `void(void *page)` |
| `apps_alarm_time_ui_create` | `0x200d1690` | `0xc53f96d` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_alarm_time_ui_destroy` | `0x200d16a8` | `0xc53f559` | `void(void *page)` |

| `apps_media_volume_ui_create` | `0x200d0ef8` | `0xc51edc5` | `void(void *page, void *root, void *data)` |
| `apps_media_volume_ui_destroy` | `0x200d0f10` | `0xc51ed21` | `void(void *page)` |

| `apps_timer_custom_ui_create` | `0x200d03dc` | `0xc5012b5` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_timer_custom_ui_destroy` | `0x200d03f4` | `0xc500c95` | `void(void *page)` |

| `settings_screenshot_ui_create` | `0x200d3ccc` | `0xc56f05d` | `void(void *page, void *root, void *data)` |
| `settings_screenshot_ui_destroy` | `0x200d3ce4` | `0xc56ef71` | `void(void *page)` |

| `health_oxygen_explanation_ui_create` | `0x200db438` | `0xc6497b9` | `uintptr_t(void *page, void *root, void *data)` |
| `health_oxygen_explanation_ui_destroy` | `0x200db450` | `0xc649081` | `void(void *page)` |

| `settings_gnss_ui_create` | `0x200d3084` | `0xc55e101` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_gnss_ui_destroy` | `0x200d309c` | `0xc55e081` | `void(void *page)` |

| `settings_wear_ui_create` | `0x200d43b4` | `0xc572575` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_wear_ui_destroy` | `0x200d43cc` | `0xc5723f1` | `void(void *page)` |

| `home_main_ui_create` | `0x200d0994` | `0xc50fb65` | `uintptr_t(void *page, void *root, void *data)` |
| `home_main_ui_destroy` | `0x200d09ac` | `0xc50fa75` | `void(void *page)` |
| `home_edit_ui_create` | `0x200d0914` | `0xc50df9d` | `uintptr_t(void *page, void *root, void *data)` |
| `home_edit_ui_destroy` | `0x200d092c` | `0xc50def5` | `void(void *page)` |
| `home_add_ui_create` | `0x200d0894` | `0xc50d501` | `uintptr_t(void *page, void *root, void *data)` |
| `home_add_ui_destroy` | `0x200d08ac` | `0xc50d109` | `void(void *page)` |

| `home_layout_ui_create` | `0x200d0b20` | `0xc511f41` | `uintptr_t(void *page, void *root, void *data)` |
| `home_layout_ui_destroy` | `0x200d0b38` | `0xc511eb9` | `void(void *page)` |
| `home_pick_ui_create` | `0x200d0a0c` | `0xc511001` | `uintptr_t(void *page, void *root, void *data)` |
| `home_pick_ui_destroy` | `0x200d0a24` | `0xc510141` | `void(void *page)` |
| `home_category_ui_create` | `0x200d0c08` | `0xc512695` | `uintptr_t(void *page, void *root, void *data)` |
| `home_category_ui_destroy` | `0x200d0c20` | `0xc5121d1` | `void(void *page)` |
| `home_sport_ui_create` | `0x200d0b94` | `0xc51282d` | `uintptr_t(void *page, void *root, void *data)` |
| `home_sport_ui_destroy` | `0x200d0bac` | `0xc5121a5` | `void(void *page)` |
| `home_choose_ui_create` | `0x200d0aa0` | `0xc511e31` | `uintptr_t(void *page, void *root, void *data)` |
| `home_choose_ui_destroy` | `0x200d0ab8` | `0xc511565` | `void(void *page)` |

| `settings_display_timeout_ui_create` | `0x200d2a6c` | `0xc557f19` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_display_timeout_ui_destroy` | `0x200d2a84` | `0xc5580fd` | `void(void *page)` |
| `settings_display_keep_awake_ui_create` | `0x200d290c` | `0xc555ee1` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_display_keep_awake_ui_destroy` | `0x200d2924` | `0xc555e2d` | `void(void *page)` |

| `settings_display_raise_mode_ui_create` | `0x200d2984` | `0xc55645d` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_display_raise_mode_ui_destroy` | `0x200d299c` | `0xc556209` | `void(void *page)` |
| `settings_display_raise_schedule_ui_create` | `0x200d2af4` | `0xc559135` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_display_raise_schedule_ui_destroy` | `0x200d2b0c` | `0xc558205` | `void(void *page)` |
| `settings_display_aod_schedule_ui_create` | `0x200d29f8` | `0xc557619` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_display_aod_schedule_ui_destroy` | `0x200d2a10` | `0xc556681` | `void(void *page)` |

| `settings_display_main_ui_create` | `0x200d273c` | `0xc552f29` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_display_main_ui_destroy` | `0x200d2754` | `0xc552135` | `void(void *page)` |
| `settings_display_aod_detail_ui_create` | `0x200d27b0` | `0xc553d51` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_display_aod_detail_ui_destroy` | `0x200d27c8` | `0xc554455` | `void(void *page)` |
| `settings_display_aod_switch_ui_create` | `0x200d2824` | `0xc554969` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_display_aod_switch_ui_destroy` | `0x200d283c` | `0xc55451d` | `void(void *page)` |

| `apps_recorder_upload_ui_create` | `0x200da6c4` | `0xc61bb69` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_recorder_upload_ui_destroy` | `0x200da6dc` | `0xc61bacd` | `void(void *page)` |
| `apps_recorder_remind_ui_create` | `0x200da650` | `0xc61b8f1` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_recorder_remind_ui_destroy` | `0x200da668` | `0xc61b569` | `void(void *page)` |
| `apps_recorder_interrupt_ui_create` | `0x200da564` | `0xc618795` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_recorder_interrupt_ui_destroy` | `0x200da57c` | `0xc618711` | `void(void *page)` |

| `health_vitality_setting_ui_create` | `0x200db840` | `0xc650e9d` | `uintptr_t(void *page, void *root, void *data)` |
| `health_vitality_setting_ui_destroy` | `0x200db858` | `0xc650ba5` | `void(void *page)` |
| `health_vitality_explanation_ui_create` | `0x200db728` | `0xc64f931` | `uintptr_t(void *page, void *root, void *data)` |
| `health_vitality_explanation_ui_destroy` | `0x200db740` | `0xc64f831` | `void(void *page)` |
| `health_vitality_hr_catalog_ui_create` | `0x200dc0b0` | `0xc668b65` | `void(void *page, void *root, void *data)` |
| `health_vitality_hr_catalog_ui_destroy` | `0x200dc0c8` | `0xc668471` | `void(void *page)` |

| `health_women_notes_ui_create` | `0x200da738` | `0xc620955` | `uintptr_t(void *page, void *root, void *data)` |
| `health_women_notes_ui_destroy` | `0x200da750` | `0xc62065d` | `void(void *page)` |

| `health_sleep_explanation_ui_create` | `0x200dafe4` | `0xc63bda9` | `uintptr_t(void *page, void *root, void *data)` |
| `health_sleep_explanation_ui_destroy` | `0x200daffc` | `0xc63bd79` | `void(void *page)` |

| `apps_worldclock_main_ui_create` | `0x200d9e98` | `0xc601859` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_worldclock_main_ui_destroy` | `0x200d9eb0` | `0xc600d6d` | `void(void *page)` |
| `apps_worldclock_add_list_ui_create` | `0x200d9e24` | `0xc6005bd` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_worldclock_add_list_ui_destroy` | `0x200d9e3c` | `0xc600411` | `void(void *page)` |
| `apps_worldclock_detail_ui_create` | `0x200d9db0` | `0xc60008d` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_worldclock_detail_ui_destroy` | `0x200d9dc8` | `0xc5ffa95` | `void(void *page)` |

| `apps_todolist_main_ui_create` | `0x200dcde4` | `0xc682bbd` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_todolist_main_ui_destroy` | `0x200dcdfc` | `0xc682971` | `void(void *page)` |
| `apps_todolist_list_ui_create` | `0x200dcd70` | `0xc681911` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_todolist_list_ui_destroy` | `0x200dcd88` | `0xc681531` | `void(void *page)` |
| `apps_todolist_detail_ui_create` | `0x200dccfc` | `0xc6814a9` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_todolist_detail_ui_destroy` | `0x200dcd14` | `0xc680cf1` | `void(void *page)` |
| `apps_todolist_sub_list_ui_create` | `0x200dce58` | `0xc683401` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_todolist_sub_list_ui_destroy` | `0x200dce70` | `0xc682ff9` | `void(void *page)` |

| `apps_phonemute_ui_create` | `0x200da8e4` | `0xc6240c5` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_phonemute_ui_destroy` | `0x200da8fc` | `0xc623dd1` | `void(void *page)` |
| `apps_find_phone_ui_create` | `0x200da99c` | `0xc625111` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_find_phone_ui_destroy` | `0x200da9b4` | `0xc625a99` | `void(void *page)` |

| `settings_main_ui_create` | `0x200d34ec` | `0xc5669ad` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_main_ui_destroy` | `0x200d3504` | `0xc566371` | `void(void *page)` |

| `settings_system_ui_create` | `0x200d3fb4` | `0xc570c89` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_system_ui_destroy` | `0x200d3fcc` | `0xc5704f9` | `void(void *page)` |

| `settings_bluetooth_ui_create` | `0x200d3300` | `0xc563c99` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_bluetooth_ui_destroy` | `0x200d3318` | `0xc562fc9` | `void(void *page)` |
| `settings_bluetooth_headphone_ui_create` | `0x200d3404` | `0xc564b25` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_bluetooth_headphone_ui_destroy` | `0x200d341c` | `0xc564621` | `void(void *page)` |

| `apps_perpetual_main_ui_create` | `0x200cf9d8` | `0xc4f35d5` | `void(void *page, void *root, void *data)` |
| `apps_perpetual_main_ui_destroy` | `0x200cf9f0` | `0xc4f2399` | `void(void *page)` |
| `apps_perpetual_day_detail_ui_create` | `0x200cf794` | `0xc4f12f9` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_perpetual_day_detail_ui_destroy` | `0x200cf7ac` | `0xc4f007d` | `void(void *page)` |
| `apps_perpetual_show_ui_create` | `0x200cfa4c` | `0xc4f6075` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_perpetual_show_ui_destroy` | `0x200cfa64` | `0xc4f3791` | `void(void *page)` |
| `apps_perpetual_schedule_ui_create` | `0x200cfac0` | `0xc4f6b85` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_perpetual_schedule_ui_destroy` | `0x200cfad8` | `0xc4f60fd` | `void(void *page)` |
| `apps_perpetual_week_ui_create` | `0x200cfb34` | `0xc4f972d` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_perpetual_week_ui_destroy` | `0x200cfb4c` | `0xc4f6e85` | `void(void *page)` |

| `settings_notify_ui_create` | `0x200d3824` | `0xc56808d` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_notify_ui_destroy` | `0x200d383c` | `0xc5676b1` | `void(void *page)` |

| `apps_mijia_main_ui_create` | `0x200d055c` | `0xc5061dd` | `uintptr_t(void *page, void *root, void *data)` |
| `apps_mijia_main_ui_destroy` | `0x200d0574` | `0xc5067dd` | `void(void *page)` |

| `settings_down_key_ui_create` | `0x200d2fe4` | `0xc55de05` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_down_key_ui_destroy` | `0x200d2ffc` | `0xc55db29` | `void(void *page)` |
| `settings_quick_gesture_ui_create` | `0x200d3124` | `0xc55f58d` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_quick_gesture_ui_destroy` | `0x200d313c` | `0xc55e439` | `void(void *page)` |
| `settings_gesture_guide_ui_create` | `0x200d3198` | `0xc55fadd` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_gesture_guide_ui_destroy` | `0x200d31b0` | `0xc55f8ad` | `void(void *page)` |

| `settings_gesture_action_ui_create` | `0x200d320c` | `0xc560f95` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_gesture_action_ui_destroy` | `0x200d3224` | `0xc55fcb1` | `void(void *page)` |
| `settings_gesture_teach_ui_create` | `0x200d3288` | `0xc5612a9` | `uintptr_t(void *page, void *root, void *data)` |
| `settings_gesture_teach_ui_destroy` | `0x200d32a0` | `0xc561265` | `void(void *page)` |

`void0` 至 `void4` 接收零至四个 32 位整数或指针参数且无返回值；`word0` 至 `word4` 接收相应参数并返回一个整数或指针字。页面值行共用原生文本入口，框架按各自的调用位置与对象槽分发。页面存活检查在每次回调分发时读取根槽，避免已经销毁的控件槽指向被复用对象时误触发。OS、系统版本、MAC 和序列号入口改变的是显示文字。图像资源参数可为路径、符号或描述符指针，模块需遵循对应的生命周期；使用 before/replace 修改参数，文字替换快捷接口仅用于标记为文本的入口。

关于本机页面会先写入根槽，再创建标签和更新值；销毁时从根槽开始清零 76 字节，包含这些标签槽。五个值文字 Hook 在调用点和标签匹配之外，也要求根槽非零。这个判断不能保证页面正在并发销毁时对象始终有效。

页面根槽的静止检查只反映对应页面状态。文本和控件标志的底层函数仍由整个系统共享：安装或恢复物理入口时，所有可能执行该函数的线程都需要静止。框架的门锁和在途计数不能证明这一条件：线程可能暂停在原函数的待覆盖指令中，也可能已经进入分发入口但尚未增加在途计数。回调型入口正常卸载或发布失败后，只要已创建分发入口，都会清除回调并保留原函数及编号；恢复失败时继续保留等待重试，恢复成功后也不复用编号。原始替换回调、运行时卸载，以及内联指令写入时的其他线程仍需独立屏障；当前不能因此保证真机安全。

卸载命名 Hook 或注销模块时，框架也会检查该 Hook 配置的页面静止槽；页面仍存活时返回 `VEP_BUSY`，关闭页面后可重试。停用模块仅旁路其回调，不恢复共享物理入口。紧急安全恢复会先旁路命名回调，跳过页面仍活跃的入口并尝试恢复其他入口；关闭相关页面后再次执行恢复。重启后的隔离仍由持久标记控制。

`settings.return_to_dial.selected_option` 读取到的值是选项编号，固件将其低 8 位转换成十进制后持久保存；当前列表构造接受的编号为 0、1、2。模块应只返回这些编号，并注意这会实际改变设置。该入口返回原生指针字，但此调用位置将其作为整数使用。

`settings.return_to_dial.event_code` 可修改回调比较的事件代码；固件仅在其等于 `7` 时进入选项保存分支。`ui.event.code` 是共享的全局读取入口，改变返回值会影响所有匹配的调用者。

事件对象的当前目标在冒泡时可能改变，原始目标保留初始对象；本固件的字段顺序与上游 LVGL 8.3 不同。事件参数的类型由具体事件决定；替换上述指针时必须满足调用者的对象类型和生命周期要求。

`ui.label.set_text`、`ui.object.set_size` 和 `ui.object.add_flag` 没有调用点或对象过滤，会作用于各系统页面和表盘对这些入口的调用。模块应自行限定范围；跳过调用或修改参数可能影响其他页面。绕过相应原生入口的调用不在其范围内。

`ui.object.clear_flag`、`ui.object.has_flag` 和 `ui.object.has_state` 同样是全局入口。标志查询要求指定的每一位都存在才返回 1；状态查询只要任一指定位存在便返回 1。修改查询结果会影响系统后续分支。

`ui.object.clean` 会删除对象的子控件；跳过该调用可能导致控件残留或页面状态异常。其跳板只针对该固件已验证的入口及前十个字节重写调用指令，因此被调用函数观察到的返回地址位于跳板；若另一个 Hook 根据该返回地址过滤，需要考虑这一变化。局部模拟验证需要 Rust 编译器和 Python 的 Unicorn 包：安装 `unicorn` 后运行 `python3 scripts/test-thumb-relocation.py`。

`ui.object.create` 的父对象可为空；第二参数可为空，非空时固件会读取其首字节。它只覆盖通过基础控件创建入口的调用，其他控件可能直接使用类创建函数。原函数失败会返回空指针，调用方未必处理空指针；模块替换返回值时必须保持对象类型、父子关系和生命周期。跳板只重写该固件的确切入口，并读取原位置的常量池；局部模拟未执行完整创建流程。

`ui.object.delete` 覆盖经过该入口的删除调用，跳过可能使资源和页面状态无法正常释放；改变对象参数必须确保对象有效。原函数执行后对象可能已释放，`after` 回调不能解引用原对象。此入口的跳板只针对该固件的确切指令重写两条条件路径；局部模拟只比较分支恢复位置与寄存器状态，不执行完整删除流程。

`ui.object.class_allocate` 返回的对象尚未执行类初始化，部分调用方会立即初始化且不检查空指针；替换类、父对象或返回值必须满足实际类布局和所有权要求。`ui.object.event_add` 的参数依次为对象、回调函数、事件过滤值和用户数据，返回事件描述符；回调与用户数据必须在注册期间保持有效。`ui.object.event_remove` 按函数指针移除第一个匹配项，返回 1 表示移除、0 表示未移除。跳过或改写这些调用会改变事件投递和数据生命周期。

`ui.object.send_event` 拦截经过该入口的对象事件发送，事件代码只使用低 16 位，参数的类型与生命周期由事件决定。固件在对象为空时返回 1；其他调用方可能检查返回状态，模块替换返回值时应遵循具体调用方约定。发送过程中可能再次触发该 Hook，模块需要处理递归。该入口高度共享，跳过事件可能影响对象销毁、输入和绘制。针对该固件的跳板重写了空对象分支，局部模拟覆盖两条分支和寄存器、栈及条件标志，不代表完整事件分发或真机已验证。

`system.navigation` 和 `system.apps` 点替换的是启动数据复制到 SRAM 的函数表槽，安装前会将槽的实时值与表内原函数指针比较。页面导航动作是调用方提供的结构指针，含目标和回调等字段；修改指针或调用原函数时必须保持实际调用方的布局及生命周期。`home` 使用整数模式并调用后台页面导航路径，因此同时挂钩时可能依次触发两个入口。终止后台应用点在长续航模式下也会使用；其返回值可能是日志函数的返回值，不能一律当作布尔结果。终止指定应用要求有效的调用方和包名字符串，固件目前接受的原因值为 0。直接调用原函数不会经过函数表槽。单次指针存储及旧分发入口保留仍不能证明卸载或运行时生命周期安全，也不证明槽不会被固件其他代码改写。

闹钟列表的 `row_index` 和 `switch_index` 必须保持为当前有效的闹钟索引；固件会把它用于解析记录，开关回调还会先解析索引，再判断事件类型。注册点覆盖正常闹钟行和可能使用其他回调的特殊行。修改回调或事件代码可能使开关界面与实际闹钟状态不一致。

闹钟自定义重复的星期索引只允许 `0..6`。固件在非法索引路径可能触发未定义指令；改变事件、索引或注册回调可能使选中状态与保存的重复规则不一致。页面销毁后 `0x20111484` 仍可能指向已释放内存，因此本表不使用该指针作为页面活跃检查。

应用列表的 `icon.app_id` 来自回调用户数据，固件按低 16 位使用。普通模式下它影响应用启动；编辑模式下同一回调可能进入应用卸载流程。更改此值需要使用已注册的正确应用 ID，并考虑当前模式；列表外的启动路径不受该点影响。

录音应用的页面注册位于地区判断分支：固件读取 `factory.board.id`，当其值为 `CN` 时不会经过所分析的注册路径。该 Hook 只覆盖已注册并实际运行的页面，具体设备状态仍需确认。

媒体控制共用回调检查事件代码 `7`，再读取当前控件关联的数据选择操作。`current_target` 返回的是控件指针，替换它必须保证对象及其关联数据有效；注册点按固件构建分支分组，不代表所有媒体控制路径。

通知聚合文字点覆盖列表更新时的应用名、标题、内容、时间和清除按钮文字。消息行注册时的用户数据是通知记录指针；替换该指针必须保证它及其记录在回调期间有效。清除按钮回调会对当前通知组执行清除操作。

遥控相机快门回调区分按下事件 `1` 和释放事件 `8`；释放可触发立即拍摄或倒计时，取决于延时设置。改写事件或跳过回调可能使视觉反馈、计时和手机端状态不一致。

声音设置的操作编号来自 `0`、`1`、`2` 三个已注册条目；这些操作会导航或改变振动设置。振动模式选择回调接收到的注册数据为 `0` 或 `1`，它被用作控件搜索上界；更大的值可能访问未初始化的控件指针。

通知中心开关回调只在用户数据为 `0` 时处理该操作。控制中心开关会写入持久化状态；修改回调或数据可能使开关显示与实际设置不一致。

活动详情卡片标题和图标调用点由多个卡片共用；它们不覆盖数值格式化或数据来源。替换图标资源时须保证资源在对象使用期间有效。

久坐提醒与久坐通知复用状态槽；按钮注册点只影响对应界面，改变回调可能使显示与提醒设置不同步。完成提示仅在提醒类型为 `17` 时创建。

活动数据说明页的章节标题和正文调用点分别由步数、热量、强度、站立四段共用；需要修改某一段时，应自行区分调用时的文字或对象。

日历详情内容可能含私人信息；地点、描述仅在原始字段非空时绘制。天气逐日预报图标调用点由多天共用，单纯替换会影响多个日期。

天气详情下拉刷新注册点只影响该页面视图的指定事件；跳过回调可能影响刷新显示与状态。

天气预警行注册点将行索引用作回调数据，详情页按索引读取预警记录；改变索引前须自行确保它有效。预警列表各行共用同一组行调用点。

秒表四个按钮的回调都依赖注册时传入的页面状态指针；替换该指针或回调须遵循相同生命周期与调用约定，否则可能导致崩溃或计时状态不一致。

手电筒模式事件处理与页面退出、动画和电量状态相关；警告图文 Hook 只改变显示，不改变电量判断。

指南针图标和校准提示只影响视图；方向数值通过可变参数格式化路径更新，这些点不修改传感器结果或校准状态。

指南针方向图标旋转角以十分之一度传入，四个旋转点只修改显示对象；传感器回调是动态注册的槽位，尚不能用现有静态槽位机制可靠接管，见 [传感器路径证据](../evidence/compass-rotation-043.json)。

压力设置的回调注册点只覆盖该页面的开关；放松提醒行显示点不修改后台设置。更改或跳过这些操作可能导致显示与实际设置不一致。

血氧低值提醒选项回调以事件数据 `4` 为扫描边界，按当前对象选择关闭、90、85 或 80；更改扫描边界或对象可能越界或造成设置与显示不一致。行显示调用点本身不改变监测状态。

睡眠设置列表的事件数据决定跳转的设置类型；问卷选项调用点由五个选项共用。修改回调或选择结果可能影响保存的设置和问卷数据。

血氧测量提示 Hook 只修改界面文字或图像，不改变测量算法和状态；错误提示可能掩盖真实测量状态。低值图表的说明入口通过事件数据传递页面参数。

呼吸练习模式列表、训练设置与会话页面的事件注册点和事件数据读取点是不同调用，动作分支与参数见证据文件。修改回调、事件数据或跳过原函数可能影响训练状态及页面退出；模式索引被用于数组访问，不能随意改成越界值。

睡眠 HRV 文本点区分说明页与信息页的不同分支；图表数据、测量算法不在这些界面调用点内。压力测量提示可能先后被覆盖；更改文本可能掩盖真实状态。压力月度日期标签只是绘制调用，不能当作历史数据本身。

心率设置目录生命周期指针位于心率页面描述符，创建与销毁函数同时被候选描述符 `0x200dc064` 使用；共享状态会影响安装时机。心率说明多段文字点在循环中触发多次；压力说明区分两种界面分支。图表与文字调用不等于底层健康数据。

运动分类与同类列表共用列表构建函数，但拥有不同描述符和私有数据；此处生命周期 Hook 绑定各自槽位。运动编辑图标在列表循环中可能多次触发，倒计时动画图像会多次更新；替换资源需保持生命周期有效。

运动设置的事件数据读取返回的是配置记录指针，后续代码会解引用并可能持久化配置；不能把它当作整数开关随意替换。数值选择器会根据设置类型采取不同分支，多个注册点可能分别对应不同布局。

运动准备页的启动回调会检查存储并进入不同运动流程；设置、热身和泳池入口的事件数据均为运动记录指针，部分路径还会解引用嵌套对象。运动实时和准备页的私有数据由公共清理函数释放；事件回调仍需在设备上确认。

热身暂停与继续按钮共用状态切换回调，结束按钮注册的事件过滤范围包含多个事件类型。星历页面是定位辅助数据更新流程，其更新入口会检查连接；文字 Hook 不改变星历数据。

番茄专注的启动、结束和确认回调会修改勿扰状态或保存时长、统计数据；拦截它们可能使状态不一致。主页面销毁时会直接解引用 `0x20111794` 指向的初始化数据：跳过创建或令初始化中途失败可能导致崩溃，应保留原创建与销毁流程。

闹钟编辑和时间确认会创建或修改闹钟，智能提醒选项也可能更新记录。其事件参数有的为页面状态指针、有的为数值选项，见证据文件；自定义及编辑页面的部分全局别名在销毁后未清零，所以这些调用点以描述符根槽限定活动范围。

媒体音量加减入口会调整当前设备或手机的音量；音量增加时某些条件下会先显示提示。页面创建入口无法由当前反编译器恢复为函数，相关地址和状态赋值以 Thumb 指令核对；创建返回值没有确认含义，按无返回值暴露。

计时器预设控件的事件数据指向时长记录，回调直接访问事件结构；自定义滚轮为事件过滤值 11 和 12 注册同一回调，注册时的数据不同；事件编号的固件语义尚未确认，不能直接套用上游 LVGL 版本的枚举。跳过开始或修改滚轮事件可能使倒计时状态和界面不同步。

计时器运行视图由主页内部创建；停止和暂停／继续按钮会修改计时状态。最近使用项回调通过事件数据读取时长记录，修改该指针或跳过状态更新可能导致状态与界面不同步。结束提示使用独立根槽。

计时器运行视图与主页的切换分别在两个对象上设置或清除标志 1 和 16；这些点只覆盖表中列出的切换调用，跳过标志操作可能使视图状态不一致。

截屏设置创建回调在根对象为空时直接返回，固件页面管理器忽略其返回值，故按无返回值暴露；开关回调还检查事件数据的低字节。

血氧说明页会依据导航数据选择不同说明分支。其应用全局根指针在销毁时不清零，相关点仅以页面描述符根槽限定，不能把该槽当成线程同步机制。

定位模式选项行和单选控件注册同一事件回调，事件数据低字节为选项编号；回调仅对编号 0、1、2 写入 `persist.gnss_mode`。修改该数据可能改变保存的定位模式。

佩戴方向设置的四个选项使用编号 0 至 3；回调直接用事件数据索引固件表，未见边界检查。不要用未经验证的值替换编号，否则可能访问无效内存。

主屏主页的四个滚动事件注册共享回调并携带状态指针；编辑页的添加和确认使用操作编号，添加页按钮携带卡片记录指针。修改或跳过交互可能使界面与卡片配置不同步。

主屏布局选择把选项位掩码写入导航数据；卡片选择页的日历预览可能使用动态分配的图片。修改布局或图片来源时须保留固件预期的数据和值的生命周期。

熄屏时间的确认流程可能写入时长或显示较长时长提示；屏幕常亮选项会影响设备常亮状态。修改事件数据可能使控件与系统状态不同步。

抬腕显示方式、抬腕亮屏时段和息屏显示时段分别注册回调并维护独立状态。修改事件数据可能改变显示或亮屏行为，并使控件和已保存设置不同步。

显示主页四个选项按操作编号导航到亮度、熄屏时间、抬腕亮屏和息屏显示；息屏显示根据当前状态进入不同子页。息屏详情中的操作会修改开关和时间设置。

录音提醒页在保存应用根槽前构建控件，相关调用以描述符根槽限定；录音中断页没有独立的可清理应用状态槽，也使用描述符根槽。两个槽位均不构成线程屏障。

活力应用页面 4 与心率设置目录共用创建、销毁函数及状态槽，但各自拥有独立的页面描述符；两个页面的状态不能视为互相独立。

女性健康说明页的四项图例共用同一组调用点；每次创建页面会分别触发四次。说明页销毁回调只记录日志，静止检查使用页面描述符根槽；异步销毁路径及真机行为尚待验证。

女性健康主页面的柱状图图片按条件选择，前后项的调用点在循环中可能多次触发；日期及状态文字的帮助函数有多个调用者，只按调用点和主页面状态限定，并不识别具体标签。柱状图帮助函数还存在延迟调用，状态槽不构成线程同步保证。

女性健康柱状图滚动结束后，旧项重置与新项选择分别走不同图片调用点；事件码和事件数据点只对应列出的回调内读取。更改事件码或指针可能破坏页面状态，页面槽不保证线程静止。

睡眠应用页面 1 的说明页与页面 8 的心率变异性说明页描述符名称同为 `explanation`，但页面 ID、状态槽及创建函数不同。

世界时钟详情页通过定时器刷新时间和星期；首次绘制与刷新使用不同调用点。列表行回调可能对多个城市重复触发，页面状态槽不保证定时器或其他线程已经停止。

待办事项列表和子列表会复用行创建与更新调用点，同一 Hook 可能针对多个事项触发；详情文字根据长度走完整或截断分支。页面槽不保证排队回调与其他线程已经停止。

查找手机销毁时若资源句柄 `0x2011cf64` 为空会提前返回，应用根槽可能保持非零；相关 Hook 同时检查应用根槽与描述符根槽，可能因此拒绝安装或卸载。共享按钮注册点可能接收不同回调，页面槽也不保证线程静止。

设置主页列表在应用状态槽赋值前可能创建行，因此其行事件点以描述符根槽限定触发，同时检查两个静止槽。列表索引对应的双布局表见[设置主页证据](../evidence/settings-main-043.json)；回调没有本地索引边界检查，修改索引可能导致越界。

系统设置行索引由回调直接用于选择动作，可能进入重启、关机或恢复出厂设置确认；三组静态动作表见[系统设置证据](../evidence/settings-system-043.json)。回调没有本地索引边界检查，页面槽也不保证线程静止。

蓝牙扫描页与耳机详情页分别使用独立状态槽；连接和取消配对按钮拥有不同事件回调，详情名称调用点可能在重绘时再次触发。页面槽不能证明扫描或异步回调已经停止。

世界时钟城市行的事件数据是城市记录指针；添加、删除和进入详情分别使用不同回调。添加回调在判断事件码之前先检查城市数量，因此仅修改事件码不能拦截所有分支。

待办事项的勾选与行点击回调通过事件数据读取索引；子列表勾选会按索引修改和重排子事项，回调没有本地边界检查。列表文字帮助函数可对不同事项重复触发。

万年历页面 1 与 4 的描述符同名但页面 ID 不同；主页与周视图的今天按钮也使用不同回调。主页按钮在读取事件码之前会修改部分状态，改写事件码无法撤销这些操作。

通知页的四个开关注册点分别对应不同固件回调；亮屏开关还会改变抬腕通知选项的可见性。注册点本身不等同于设置读取或写入函数。

米家主页分别登记蓝牙断开、App 断开分支及多家庭标题；加载页辅助函数由多个调用方共享，不能视为仅属于主页。订阅响应和计时器可能与页面销毁并发，状态槽不提供线程同步。

快捷手势说明的五段文字在创建和语言变更时共用同一组调用点；页面状态槽不保证其他线程或排队的回调已经停止。

下按键选项点击会按事件索引查表并保存对应功能；`settings.down_key.selected_index` 的替代值必须在当前列表范围内，固件未在该回调中验证索引，越界可能造成崩溃。改变回调注册也可能影响设置和界面的同步。

快捷手势页面的关闭态和开启态使用不同的回调与注册调用点；页面重建时可能再次触发。注册点可以影响开关和跳转行为，但并不是手势状态写入函数。

手势功能设置会用点击索引访问功能表并写入对应手势的持久设置；`settings.gesture_action.selected_index` 替代值必须同时在当前列表和功能表范围内。训练过程存在定时器和订阅，状态槽不保证回调已经停止。

页面生命周期点通过各自页面描述符的回调槽拦截 UI 创建或 UI 销毁。创建时参数依次为页面、根对象和导航数据，固件生命周期调用方忽略创建函数的返回值；销毁时参数为页面。创建前页面状态槽可能尚未填充，因此分发仅依赖该描述符槽；安装和卸载检查各点指定的静止槽；多数页面同时检查页面状态槽和页面描述符根槽，血氧说明页、录音中断页及女性健康说明页仅检查描述符根槽。运动列表等页面的静止槽包含描述符私有数据指针；具体槽位见每个点的适配表。页面管理器在调用创建回调前设置描述符根槽，并在 UI 销毁后清空。每个点的 `field("page_id")` 与 `field("app_id")` 分别读取页面结构偏移 20、22 的 16 位值。跳过创建或销毁可能破坏页面、遗留资源或回调；根槽不能保证其他线程静止。

当前 143 条生命周期静止槽清理位置见[生命周期状态槽审计](../evidence/lifecycle-state-audit-043.json)。这些位置来自固件销毁路径及页面管理器的静态检查；若模块跳过销毁、执行中断或发生并发访问，不能据此假定清理已经完成。

通知详情和聚合页面的创建函数会解引用第三个参数；模块若修改导航数据，必须保证指针及其指向的数据在原函数执行时有效。日历页面创建函数产生的返回寄存器可能包含时间值，但已观察到的生命周期调用方忽略该返回值，`word3` 接口仅传递一个字，不应将它当作完整时间返回值。

五个接受导航动作指针的入口提供 Python `field()`：`page_id` 是偏移 4 的 16 位值，`app_id` 是偏移 6 的 16 位值，`source` 是偏移 8 的 8 位输入值。源码中的结构长度为 44 字节；`source` 随后会被固件归一化。部分页面的初始编号见[导航页面 ID 对照表](navigation-page-ids-xiaomi-band-10-pro-3.101.043.md)；字段分析见 [system-navigation-043.json](../evidence/system-navigation-043.json)。

三个设置页面的 `*_register` 入口只覆盖各自的事件注册调用，参数依次是对象、回调、事件代码和用户数据，事件代码均为 7。返回表盘选项的用户数据是行编号 0、1、2；NFC 为 0，长续航为 1。这三个调用方均忽略事件描述符返回值。跳过注册会影响对应控件的交互，但不能阻止其他路径修改设置，控件显示也可能需要同步。页面根槽只限定分发范围，不能保证共享入口的其他线程在安装或卸载期间静止。

亮度页面的三个注册点也使用事件代码 7，用户数据分别为自动亮度 `0`、阳光模式 `1`、手动亮度入口 `2`；调用方不使用返回的事件描述符。`action_data` 读取共用回调中的操作编号：修改它可能改变实际亮度或持久化设置；非零且不等于 1 的值进入另一分支，不能作为通用跳过手段。跳过一个注册只影响对应控件，显示状态可能需要同步。安装和卸载要求页面根槽及状态槽都为空，回调仅在根槽非零时分发；这些检查不能证明共享目标的其他线程静止。

勿扰与睡眠设置页的两个说明文字在页面创建及重建时赋值。勿扰时间行注册事件代码 7、用户数据 0，回调只在数据低字节为 0 时导航；睡眠开关注册事件代码 7、用户数据 1，其回调根据开关状态修改持久设置并通知睡眠模式服务。拦截开关回调可能导致控件外观与实际状态不一致；拦截勿扰时间行仅影响该导航入口。页面根槽和调用位置不提供共享物理入口的线程屏障。

NFC 开关回调仅在事件代码为 `7` 且点击数据低字节为 `0` 时执行开关处理。修改这两个读取结果可跳过该次回调的开关分支，但不影响其他 NFC 控制路径；控件的显示状态也可能需要另行同步。

`settings.battery.long_mode_click_data` 原值为 1；返回其他值会让该次点击处理跳过长续航分支。控件可能已先改变显示状态，需要模块另行处理显示同步；这也不能阻止其他路径改变长续航模式。`ui.event.user_data` 则作用于所有调用该公共函数的页面，返回值可能是指针，必须遵循对应调用方的数据约定。

`watchface.dual_time.selected_index` 使用此固件时区表的索引 `0` 至 `42`；超出范围的无符号值会被固件归为 `0`。索引对应固件内的列表顺序，跨版本不能假定时区相同。

`watchface.selection` 的文字点只改变对应调用写出的显示文字，不修改实际表盘或排序。预览名称对应创建的各张卡片；拖动位置文字只覆盖进入拖动时的一次赋值，后续更新可能经过其他调用点。事件代码点只影响各自的回调，修改代码可能令拖动状态不一致，或者让固件按不兼容的事件数据进入其他分支。普通表盘与息屏表盘选择流程共用部分调用，具体是否触发取决于页面模式。

`watchface.sport_selection.item_data` 返回当前条目指针。返回 `0` 会使这次回调直接退出；非零替代值必须指向存活且布局兼容的条目。安装检查要求分类页和运动页的根槽同时为零，回调分发要求至少一个根槽非零。

`apps.mijia.scene.selected_index` 的替代值会改变实际执行的米家场景，必须为当前场景列表中有效的非负索引。固件使用有符号上界比较，负数可能使访问落在列表之前；不要用越界索引来跳过场景执行。

上述双时区、表盘运动选择和米家场景注册点的参数依次是对象、回调、事件代码 7、用户数据。双时区和米家使用行索引，运动选择使用条目指针。双时区和运动选择的更新函数会将注册返回的事件描述符返回给调用方；替换返回值须满足上层调用约定。米家创建、更新各有两个分支，固件在更新时先移除旧回调再注册新回调，因此只拦截创建并不能覆盖后续更新。跳过注册可使对应行不可操作，但不能阻止其他入口执行场景或修改设置；页面状态不构成共享物理入口的线程屏障。

运动列表编辑回调在事件代码为 `4` 时按数据低字节选择分支：`0` 完成、`1` 删除、`2` 标记。其他低字节值会跳过这三个分支。不同分支对事件目标的布局有不同假设，不应把一种操作直接改成另一种操作。

三个运动编辑注册点分别覆盖标记、删除与完成按钮；拦截注册可能使对应按钮无法操作。首次构建时，编辑数据槽已经设置但页面根槽尚未设置，因此分发检查使用数据槽；安装和卸载检查要求数据槽及页面根槽均为空。这些条件不能证明共享事件注册函数的其他线程已静止。

心率主页面这四个入口只修改状态文案，不改变测量数值、提醒或健康数据。页面状态对象动态分配，按调用点和存活状态过滤；其中“测量中”包含两个调用点。

`health.heart_rate.action_id` 覆盖心率应用中共用该回调的多个视图。主列表中 `0`、`1` 分别对应静息心率和设置；设置列表的 `8`、`9`、`10`、`11` 分别对应监测、健康监测、高心率提醒和低心率提醒。框架不能据此判断具体来源页面；修改编号可能触发其他导航或副作用，越界编号也仍会发出导航请求。

`health.heart_rate.setting.option_search_limit` 是查找选中行的上界，并非选中项编号；修改它可能选择错误设置或造成数组越界。提醒界面的注册点只影响各自按钮的回调注册。`dismiss_type` 的 `3`、`4`、`5` 分别用于高、低和 AF 提醒；其他值仍会发送命令并关闭提醒，不能用作安全的跳过方式。改变这些逻辑可能影响实际健康提醒，而不仅是显示文字。

调度器线程遍历、异常入口和保存的 PC/LR 字段已有静态研究线索，见 [thread-quiescence-043.json](../evidence/thread-quiescence-043.json)。该线索尚未用作运行时屏障；还须覆盖分发入口、跳板和原始替换回调，并验证任务状态、并发处理器、异常上下文及返回路径。

表盘主页面的静态调用链记录在 [watchface-candidates-043.json](../evidence/watchface-candidates-043.json)。主页面容器在销毁时被保留，不能当作关闭页面的判断条件，相关候选目前尚未加入命名表。

心率设置的共用操作回调记录在 [heart-rate-candidates-043.json](../evidence/heart-rate-candidates-043.json)。该回调也由其他心率页面注册，还需要确认事件目标的归属，才能限定为设置页面的 Hook。

当前表容量为 2048 个命名点，名称通过哈希索引查找；物理 Hook 分发编号共 32 个，每个物理点最多 32 个回调，命名回调合计最多 256 个。多个名称可以共用一个物理入口。为保护迟到的分发调用，回调型入口卸载后仍占用编号，本次运行期间不能复用；原生自检也会占用一个编号。耗尽时返回 `VEP_CAPACITY`，需重启设备后重新开始。`python3 vep.py hooks` 显示当前实际配置，调用约定与 Python 规则见 [Python SDK](python-sdk.md)。

目录容量扩展前后的 ARM 常驻段大小与验证范围见[容量记录](../evidence/catalog-capacity-043.json)；构建大小不能证明真机可用内存或加载成功。

后续按系统页面与服务持续调查显示、设置、应用、表盘、交互、设备状态和运动健康等入口。加入表前记录具体调用点、ABI、对象生命周期、安装静止条件和回退证据；用途尚未确认的地址保留在分析证据中。
