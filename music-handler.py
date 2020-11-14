import obspython as obs
import os

text_source_name = ""
song_directories = ""
target_scene = ""
group_name = ""
create_playlist = False
song_number = 0
props = None

def update_text():
    song = get_active_song()
    song_name = obs.obs_source_get_name(song)
    settings = obs.obs_data_create()
    text_source = obs.obs_get_source_by_name(text_source_name)
    if text_source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", song_name)
        obs.obs_source_update(text_source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(text_source)

def get_active_song():
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_name = obs.obs_source_get_name(source)
            source_id = obs.obs_source_get_unversioned_id(source)
            active = obs.obs_source_active(source)
            if source_id == "ffmpeg_source" and active is True:
                return source

def create_playlist(props, song_number):
    for i in range(1, song_number):
        obs.obs_properties_add_int(props, "priority" + str(i), "Priority of song: " + str(i), 0, 100, 0)
        print(i)
            
def scan_folder():
    global target_scene
    global group_name
    song_number = 0
    scene = scene_name_to_scene(target_scene)
    group = obs.obs_scene_find_source(scene, group_name)
    if group is not None:
        obs.obs_sceneitem_remove(group)
        obs.obs_sceneitem_release(group)
    group = obs.obs_scene_add_group(scene, group_name)
    for file in os.listdir(song_directories):
        if file.endswith((".mp3", ".webm", ".m4a", ".ogg")):
            settings = obs.obs_data_create()
            obs.obs_data_set_string(settings, "local_file", song_directories + "/" + file)
            obs.obs_data_set_string(settings, "group", group_name)
            source = obs.obs_source_create("ffmpeg_source", file, settings, None)
            scene_item = obs.obs_scene_add(scene, source)
            group = obs.obs_scene_get_group(scene, group_name)
            obs.obs_sceneitem_group_add_item(group, scene_item)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)
            song_number = song_number + 1
    group_source = obs.obs_sceneitem_get_source(group)
    return song_number

def obs_source_print_json(source):
    settings = obs.obs_source_get_settings(source)
    json = obs.obs_data_get_json(settings)
    print(json)

def scene_name_to_scene(scene_name):
    source = obs.obs_get_source_by_name(scene_name)
    if source is not None:
        scene = obs.obs_scene_from_source(source)
        obs.obs_source_release(source)
        return scene
    else:
        obs.obs_source_release(source)
        return None
            
def signal_receiver(cd):
    update_text()

def button_handler(props, prop):
    global song_number
    song_number = scan_folder()
    global create_playlist
    create_playlist = True
    script_properties()
            
#----------------------------------------------------------------

def script_description():
    return "Song manager that allows you to scan folders and add all the music in there as sources in a group. It also lets you display the name of the source for credit. Made by Mega64."

def script_properties():
    global create_playlist
    if create_playlist is False:
        global props
        props = obs.obs_properties_create()
        source_list = obs.obs_properties_add_list(props, "text_source_list", "Source List", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
        sources = obs.obs_enum_sources()
        if sources is not None:
            for source in sources:
                source_id = obs.obs_source_get_unversioned_id(source)
                if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                    source_name = obs.obs_source_get_name(source)
                    obs.obs_property_list_add_string(source_list, source_name, source_name)
        obs.obs_properties_add_path(props, "path", "List of reproduction folder", obs.OBS_PATH_DIRECTORY, None, None)
        obs.obs_properties_add_text(props, "scene", "Target scene", obs.OBS_TEXT_DEFAULT)
        obs.obs_properties_add_text(props, "group", "Target group name", obs.OBS_TEXT_DEFAULT)
        obs.obs_properties_add_button(props, "refresh", "Refresh folder", button_handler)
        obs.source_list_release(sources)
        return props
    else:
        global song_number
        for i in range(1, song_number):
            obs.obs_properties_add_int(props, "priority" + str(i), "Priority of song: " + str(i), 0, 100, 0)
            print("¿Hola?")
        return props

def script_update(settings):
    global song_directories
    global text_source_name
    global target_scene
    global group_name
    song_directories = obs.obs_data_get_string(settings, "path")
    text_source_name = obs.obs_data_get_string(settings, "text_source_list")
    target_scene = obs.obs_data_get_string(settings, "scene")
    group_name = obs.obs_data_get_string(settings, "group")
    update_text()

def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "text_source_list", "No text source selected")

def script_unload():
    global target_scene
    global group_name
    scene = scene_name_to_scene(target_scene)
    group = obs.obs_scene_find_source(scene, group_name)
    if group is not None:
        obs.obs_sceneitem_remove(group)
    

def script_load(settings):
    global create_playlist
    create_playlist = False
    signal_handler = obs.obs_get_signal_handler()
    obs.signal_handler_connect(signal_handler, "source_activate", signal_receiver)
    obs.signal_handler_connect(signal_handler, "source_deactivate", signal_receiver)
    update_text()
    
