import superannotate as sa
import json
import objectpath
from typing import List, Dict, Union

import configs
from user import User


def make_image_comparison_html(target_folders: List[str],
                               target_image: str,
                               include_overlay: bool = False,
                               ) -> Dict[str, str]:

    """download images and table_content, and return html strings for showing downloaded images and table_content"""

    sa.init(str(configs.Paths.superannotate_config_path))

    fuse_image_file_names = []
    classes_used = []
    person2class_names = {}

    # check annotation status and skip person if annotation is not started
    persons = []
    for person in target_folders:
        img_meta_dict = sa.get_image_metadata(configs.ImageComparison.project + '/' + person, target_image)
        if img_meta_dict['annotation_status'] != 'NotStarted':
            persons.append(person)

    # loop through specified people/folders
    for person in persons:

        # download original image, annotations json, overlay image and fuse image
        sa.download_image(configs.ImageComparison.project + '/' + person,
                          target_image,
                          configs.Paths.downloads,
                          include_annotations=True,
                          include_fuse=True,
                          include_overlay=include_overlay)
        sa.download_annotation_classes_json(configs.ImageComparison.project,
                                            configs.Paths.downloads)

        # a fused image may not be downloaded if it is not yet available. so we skip handling of fuse
        fuse_name = target_image + '___fuse.png'
        if (configs.Paths.downloads / fuse_name).exists():
            # change name of fuse image to avoid overwriting image during second loop
            new_fuse_name = person + '_' + fuse_name
            fuse_image_file_names.append(new_fuse_name)
            (configs.Paths.downloads / fuse_name).rename(configs.Paths.downloads / new_fuse_name)

        # change name of pixel file to avoid overwriting
        pixel_name = target_image + '___pixel.json'
        new_pixel_name = person + '_' + pixel_name
        (configs.Paths.downloads / pixel_name).rename(configs.Paths.downloads / new_pixel_name)

        # get class names from pixel file
        with (configs.Paths.downloads / new_pixel_name).open('r') as pixel_file:
            tree_obj = objectpath.Tree(json.load(pixel_file))
        class_names = list(tree_obj.execute('$..className'))
        person2class_names[person] = class_names

        # examples:
        # class_names = ('wall', 'wall', 'door', 'furniture', 'bag', ...)
        # person2class_names = {'andrew': ['wall', 'wall', ...], 'person2': ['wall', ...]}
        # person2class_name2class_count = {'andrew': {'wall': 3, 'door': 1, 'furniture': 1, ...} ,
        #                      'layla': {'wall': 1, 'door': 0, 'furniture': 0, ...}}

        # collect all classes used (with repeats) (so it can be iterated over)
        for class_name in class_names:
            classes_used.append(class_name)

    # count class name by person and class
    person2class_name2class_count = {}
    for person in persons:
        person2class_name2class_count[person] = {}
        for class_name in classes_used:
            if class_name not in person2class_name2class_count[person]:
                person2class_name2class_count[person][class_name] = person2class_names[person].count(class_name)

    # make list of unique class names (to avoid duplicate rows in html table)
    unique_classes = set(classes_used)

    if not (configs.Paths.downloads / 'classes.json').exists():
        return {}

    # make dictionary with classes as key and colors as values
    with (configs.Paths.downloads / 'classes.json').open('r') as classes_file:
        tree_obj2 = objectpath.Tree(json.load(classes_file))
    class2color = {class_name: color_code
                   for class_name, color_code in zip(tree_obj2.execute('$..name'), tree_obj2.execute('$..color'))}

    ####################################
    # create html for table
    ####################################

    # class_colors = {'furniture': '#13dc23', 'big appliance': '#f675b3', ...}

    table_content = ""

    # make columns
    table_content += "<th>" + 'Object Class' + "</th>"
    table_content += "<th>" + 'Color' + "</th>"
    for person in target_folders:
        table_content += "<th>" + str(person) + "</th>"

    # make rows
    table_content += "<tr>"
    for class_used in unique_classes:
        table_content += "<td>" + str(class_used) + "</td>"
        if class_used in class2color:
            table_content += "<td bgcolor=" + str(class2color[class_used]) + ">" + "</td>"
        for person in person2class_name2class_count:
            row_tuple2 = person2class_name2class_count[str(person)]
            table_content += "<td>" + str(str(row_tuple2[str(class_used)])) + "</td>"
        table_content += "<tr>"
    table_content = "<table border=1>" + table_content + "<table>"

    table_html = f"<table border = '1'>{table_content}</table>"

    ####################################
    # create html for fuse_images
    ####################################

    fuse_images_html = ''
    for image in fuse_image_file_names:
        html_str2 = f'<img src="/{configs.Paths.downloads / image}" style="width:288px;height:216px;">'
        fuse_images_html += html_str2

    return {'table_html': table_html,
            'fuse_images_html': fuse_images_html}


def find_target_folders(target_image, user):

    # necessary before using any superannotate functionality
    sa.init(str(configs.Paths.superannotate_config_path))

    annotators = get_annotator_emails(user)

    big_folder_data = sa.search_folders(configs.ImageComparison.project,
                                        return_metadata=True)
    # make target_folders
    target_folders = []
    for folder_data in big_folder_data:
        folder_name = folder_data['name']
        img_meta_list = sa.search_images(configs.ImageComparison.project + '/' + folder_name,
                                         image_name_prefix=target_image,
                                         return_metadata=True)

        annotator_emails = []
        for image_dict in img_meta_list:
            annotator_email = image_dict['annotator_id']
            if annotator_email in annotators:
                target_folders.append(folder_name)
                annotator_emails.append(annotator_email)

        for email in annotator_emails or ['not-found']:
            print(f'annotator={email:<24}  target_folder={folder_name:<24} for {target_image}')

    return target_folders


def get_annotator_emails(user: User):

    # TODO remove - only for debugging
    if user.id == 'ph':
        return ['gotoole2@illinois.edu',
                'mstill2@illinois.edu',
                'ppaun2@illinois.edu',
                'julieyc3@illinois.edu',
                'karenmn2@illinois.edu',
                ]

    elif user.id == 'yushang4@illinois.edu':
        return ['gotoole2@illinois.edu',
                'mstill2@illinois.edu',
                'ppaun2@illinois.edu',
                'julieyc3@illinois.edu']

    elif user.id == 'tkoropp2@illinois.edu':
        return ['mtam6@illinois.edu',
                'janayf2@illinois.edu',
                'acw4@illinois.edu',
                'tyzhao2@illinois.edu']

    elif user.id == 'dharve5@illinois.edu':
        return ['laylaic2@illinois.edu',
                'mstill2@illinois.edu',
                'karenmn2@illinois.edu',
                'asevers2@illinois.edu']
    else:
        raise AttributeError('No matching user.id')