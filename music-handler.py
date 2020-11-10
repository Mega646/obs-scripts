import obspython as obs

text_source_name = ""

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

def signal_receiver(cd):
    update_text()
            
#----------------------------------------------------------------

def script_description():
    return "Creates a text source that is constantly actualized with the credits for whatever cp free song you're streaming"

def script_properties():
    props = obs.obs_properties_create()
    properties = obs.obs_properties_add_list(props, "text_source_list", "Source List", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                source_name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(properties, source_name, source_name)
    obs.source_list_release(sources)
    return props

def script_update(settings):
    global text_source_name
    text_source_name = obs.obs_data_get_string(settings, "text_source_list")
    update_text()

def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "text_source_list", "No text source selected")

def script_load(settings):
    signal_handler = obs.obs_get_signal_handler()
    obs.signal_handler_connect(signal_handler, "source_activate", signal_receiver)
    obs.signal_handler_connect(signal_handler, "source_deactivate", signal_receiver)
    update_text()
