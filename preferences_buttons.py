"""Copyright (c) 2020, Josh Ball of Flowstate Creative Solutions"""


FeelButtons = {}
FeelList = []

AudioButtons = {'driver type': {'XY': (1200, 318),
                                'Type': 'Menu',
                                'Box': (1012, 311, 1195, 321)
                                },
                'audio input': {'XY': (1200, 342),
                                'Type': 'Menu',
                                'Box': (1012, 335, 1195, 345)
                                },
                'audio output': {'XY': (1200, 363),
                                 'Type': 'Menu',
                                 'Box': (1012, 356, 1180, 366)
                                 }
                }
AudioList = list(AudioButtons.keys())

MIDIButtons = {'control surface one': {'XY': (943, 402),
                                       'Type': 'Menu',
                                       'Box': (854, 396, 939, 406)},
               'input one': {'XY': (1046, 402),
                             'Type': 'Menu',
                             'Box': (955, 396, 1041, 406)},
               'output one': {'XY': (1147, 402),
                              'Type': 'Menu',
                              'Box': (1057, 396, 1143, 406)},

               'control surface two': {'XY': (943, 418),
                                       'Type': 'Menu',
                                       'Box': (854, 411, 939, 421)},
               'input two': {'XY': (1046, 418),
                             'Type': 'Menu',
                             'Box': (955, 411, 1041, 421)},
               'output two': {'XY': (1147, 418),
                              'Type': 'Menu',
                              'Box': (1057, 411, 1143, 421)},

               'control surface three': {'XY': (943, 434),
                                         'Type': 'Menu',
                                         'Box': (854, 427, 939, 437)},

               'input three': {'XY': (1046, 434),
                               'Type': 'Menu',
                               'Box': (955, 427, 1041, 437)},

               'output three': {'XY': (1147, 434),
                                'Type': 'Menu',
                                'Box': (1057, 427, 1143, 437)},

               'control surface four': {'XY': (943, 450),
                                        'Type': 'Menu',
                                        'Box': (854, 442, 939, 452)},
               'input four': {'XY': (1046, 450),
                              'Type': 'Menu',
                              'Box': (955, 442, 1041, 452)},
               'output four': {'XY': (1147, 450),
                               'Type': 'Menu',
                               'Box': (1057, 442, 1143, 452)},

               'control surface five': {'XY': (943, 466),
                                        'Type': 'Menu',
                                        'Box': (854, 457, 939, 467)},
               'input five': {'XY': (1046, 466),
                              'Type': 'Menu',
                              'Box': (955, 457, 1041, 467)},
               'output five': {'XY': (1147, 466),
                               'Type': 'Menu',
                               'Box': (1057, 457, 1143, 467)},

               'control surface six': {'XY': (943, 482),
                                       'Type': 'Menu',
                                       'Box': (854, 472, 939, 482)},
               'input six': {'XY': (1046, 482),
                             'Type': 'Menu',
                             'Box': (955, 472, 1041, 482)},
               'output six': {'XY': (1147, 482),
                              'Type': 'Menu',
                              'Box': (1057, 472, 1143, 482)},

               }
MIDIList = list(MIDIButtons.keys())
FileButtons = {}
FileList = list(FileButtons.keys())
LibraryButtons = {}
LibraryList = LibraryButtons.keys()
PluginsButtons = {}
PluginsList = PluginsButtons.keys()
RecordButtons = {}
RecordList = RecordButtons.keys()
LicenseButtons = {}
LicenseList = LicenseButtons.keys()
