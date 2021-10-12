import superannotate as sa
import json
import objectpath
import os
from typing import List

import configs


def make_image_comparison_html(target_folders: List[str],
                               target_image: str,
                               ) -> str:

    """generate html string"""

    sa.init(configs.Paths.superannotate_config_path)

    # create empty list of renamed images and classes_used; create empty dict of class tuples
    renamed_image_file_names = []
    classes_used = []
    class_tuples = {}

    # loop through specified people/folders
    for person in target_folders:

        # download original image, annotations json, overlay image and fuse image
        sa.download_image('new_annotator_practice/' + person, target_image, configs.Paths.downloads, True, True, True)
        sa.download_annotation_classes_json('new_annotator_practice', configs.Paths.downloads)

        # change name of fuse image to avoid overwriting image during second loop
        # (since otherwise they would have same name)
        fuse_name = target_image + '___fuse.png'
        fuse_src = configs.Paths.downloads / fuse_name
        new_fuse_name = person + '_' + fuse_name
        fuse_dst = configs.Paths.downloads / new_fuse_name
        renamed_image_file_names.append(new_fuse_name)
        os.rename(fuse_src, fuse_dst)

        # change name of annotations json to avoid overwriting
        anno_name = target_image + '___pixel.json'
        anno_src = configs.Paths.downloads / anno_name
        new_anno_name = person + '_' + anno_name
        anno_dst = configs.Paths.downloads / new_anno_name
        os.rename(anno_src, anno_dst)

        # load json annotation file
        with anno_dst.open('r') as json_file:
            annotations = json.load(json_file)
        tree_obj = objectpath.Tree(annotations)

        # make tuple of class names from json
        class_Name_tuple = tuple(tree_obj.execute('$..className'))
        # class_Name_tuple = ('wall', 'wall', 'door', 'furniture', 'bag', ...)
        class_tuples[person] = class_Name_tuple
        # class_tuples = {'andrew': ('wall', 'wall', ...), 'person2': ('wall', ...)}

        # make list of all classes used (with repeats) (so it can be iterated over)
        for class_Name in class_Name_tuple:
            classes_used.append(class_Name)
            # classes_used = ['wall', 'wall', 'door', ...]

    # make dictionary of dictionaries of people's instance counts
    class_Name_dict = {}
    for person in target_folders:
        class_Name_dict[person] = {}
        for class_Name in classes_used:
            if class_Name not in class_Name_dict[person]:
                class_Name_dict[person][class_Name] = class_tuples[person].count(class_Name)

    # class_Name_dict = {'andrew': {'wall': 3, 'door': 1, 'furniture': 1, ...} ,
    #                   'layla': {'wall': 1, 'door': 0, 'furniture': 0, ...}}
    # make list of unique class names (to avoid duplicate rows in data table)
    unique_classes = set(classes_used)

    # unique_classes = ['bag', 'big appliance', 'door', ...]
    # open class colors json
    json_file2 = (configs.Paths.downloads / 'classes.json').open('r')
    colors_json = json.load(json_file2)
    tree_obj2 = objectpath.Tree(colors_json)

    # make tuple of all class names in project from json
    # make tuple of all color hex codes from json
    class_Name_tuple2 = tuple(tree_obj2.execute('$..name'))
    class_Color_tuple = tuple(tree_obj2.execute('$..color'))

    # make dictionary with classes as key and colors as values
    class_colors = {}
    for i in range(len(class_Name_tuple2)):
        class_colors[class_Name_tuple2[i]] = class_Color_tuple[i]

    # class_colors = {'furniture': '#13dc23', 'big appliance': '#f675b3', ...}
    # make data table
    data = ""

    # make columns
    data += "<th>" + 'Object Class' + "</th>"
    data += "<th>" + 'Color' + "</th>"
    for person in target_folders:
        data += "<th>" + str(person) + "</th>"

    # make rows
    data += "<tr>"
    row_tuple = class_Name_dict[str(target_folders[0])]
    for class_used in unique_classes:
        data += "<td>" + str(class_used) + "</td>"
        if class_used in class_colors:
            data += "<td bgcolor=" + str(class_colors[class_used]) + ">" + "</td>"
        for person in class_Name_dict:
            row_tuple2 = class_Name_dict[str(person)]
            data += "<td>" + str(str(row_tuple2[str(class_used)])) + "</td>"
        data += "<tr>"
    data = "<table border=1>" + data + "<table>"

    ####################################
    # create html
    ####################################

    res = ''  # html string

    # write original image with proper orientation/dimensions
    html_str1 = f"""
        <html>
        <head>
        </head>
        <body>
        <img src= "/{configs.Paths.downloads / target_image}" style="width:288px;height:216px;">
        <div>
            <br> 
            <spacer type="vertical" width="10" height="1">  </spacer>
            <br> 
        </div>
        """
    res += html_str1

    # write fuse images (with proper orientation)
    for image in renamed_image_file_names:
        html_str2 = f'<img src="/{configs.Paths.downloads / image}" style="width:288px;height:216px;">'
        res += html_str2

    # write data table
    html_str_last = f"""
    <table border = '1'>
    "{data}"
    </table>
    </body>
    </html>
    """

    res += html_str_last

    return res
