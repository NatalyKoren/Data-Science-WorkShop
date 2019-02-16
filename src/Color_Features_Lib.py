###########
# Imports #
###########

import textwrap
import numpy as np
import Text_Features_Lib

###########
# Globals #
###########

#Should be updated by the user. 
main_colors = { }

#############
# Functions #
############

def get_rgd_from_str(str_color):
    '''
    Get triple of R,G,B for hex color.
    Example: FFFFFF --> (255,255,255)
    '''
    R,G,B = [int(hex_color,16) for hex_color in textwrap.wrap(str_color, 2)]
    return (R,G,B)

def nearest_color(str_color, dict_colors = None):
    ''' 
    Get nearest color for str_color from dict_colors.
    if dict_colors is None: get color from main_colors dict.
    '''
    if dict_colors is None:
        dict_colors = main_colors
    str_color = str(str_color)
    if len(str_color) != 6:
        # nan value
        return 0
	# rgb_color is triple of R,G,B values.	
    rgb_color = get_rgd_from_str(str_color)
    #this is the maximum possible distance
    min_dustance = 765
    best_color = ''
	# get nearest color to rgb_color from dict_colors
    for (color,color_name) in dict_colors.items():
        distance = np.absolute(np.subtract(rgb_color,color))
        total_distance = np.sum(distance)
        if total_distance < min_dustance:
            min_dustance = total_distance
            best_color = color_name
            
    return best_color

def map_color_to_str(color):
    '''
    cast color to string
    '''
    if (type(color) is int or type(color) is float):
        try:
            str_color = str(int(color))[0:7]
        except Exception as e:
            str_color = str(color)    
    else:
        str_color = str(color)
    return str_color

def Bin_Feature_By_Colors(df, feature_name, apply_str = False, use_dict = None):
    ''' 
	This function performes binning to feature_name of colors. 
	It is used for general binning from main_colors dict or for top colors binning from relevant dict. 
	Params:
	  apply_str is for features that need to be casted to string (some values is float)
	  use_dict is for binning to top colors.
	Return:
	  new feature name
	'''
    # Create feature name 
    if use_dict is not None:
        new_feature_name = '{0}_top_colors'.format(feature_name)
    else:
        new_feature_name = '{0}_binning'.format(feature_name)
    
	# Cast to string if needed
    if apply_str:
        str_feature_name = '{0}_str'.format(feature_name)
        df[str_feature_name] = df[feature_name].apply(map_color_to_str)
        apply_nearest_color = str_feature_name
    else:
        apply_nearest_color = feature_name
    
	# Binning by nearest color
    df[new_feature_name] = df[apply_nearest_color].apply(lambda x: nearest_color(x,use_dict))
    
    Text_Features_Lib.add_correlation_to_dict(df, feature_name, new_feature_name)
    
    if apply_str:
        df.drop(str_feature_name, axis = 1, inplace = True)
    
    return new_feature_name

def Bin_Feature_By_Top_Colors(df, main_feature_name, bin_color_feature_name, n_colors = 6, apply_str_func = False):
    ''' 
	bin_color_feature_name is main_feature_name after performing binning by main_colors dict.
	Now we get the top n_colors and perform new binning from those colors. 
	'''
    # get top n_colors 
    top_color = df[bin_color_feature_name].value_counts().nlargest(n=n_colors).index
	# create a dict of top n_colors
    best_colors_dict = {k:v for (k,v) in main_colors.items() if v in top_color}
	# perform binning of main_feature_name by best_colors_dict colors
    return Bin_Feature_By_Colors(df, main_feature_name, apply_str = apply_str_func, use_dict = best_colors_dict)

def Prepare_Color_Features(df, feature_name, most_common_values_dict, apply_str_map):
    ''' 
	This function takes feature_name and create all possible features from it. 
	most_common_values_dict is dictionary of most common values. 
	All missing values of the color features is of bot accounts. 
	Therefore we will replace the missing values by bots mode.
	Return all new features names. 
	'''
	# Add the regular new features from text feature
    general_new_features = Text_Features_Lib.Add_Numeric_Features_From_Str(df, 
                                                                           feature_name, 
                                                                           most_common_values_dict, 
                                                                           replace_by_len = False)
    
	# Bin by main colors
    feature_name_binning = Bin_Feature_By_Colors(df, feature_name, apply_str = apply_str_map)
    # Replace missing values by mode
    feature_name_binning_mode = Text_Features_Lib.Replace_Missing_Values_by_Mode(df, 
                                                                                 feature_name, 
                                                                                 feature_name_binning)
    
    # Replace missing values by distribution
    feature_name_binning_dist = Text_Features_Lib.Replace_Missing_Values_by_Distribution(df, 
                                                                                         feature_name, 
                                                                                         feature_name_binning)

    # Binning by top colors
    feature_name_top_colors = Bin_Feature_By_Top_Colors(df, feature_name, feature_name_binning, 
                                                        n_colors = 3, apply_str_func = apply_str_map)
    
    # Replace missing values by mode
    feature_name_top_colors_mode = Text_Features_Lib.Replace_Missing_Values_by_Mode(df, 
                                                                                    feature_name, 
                                                                                    feature_name_top_colors)
    # Replace missing values by distribution
    feature_name_top_colors_dist = Text_Features_Lib.Replace_Missing_Values_by_Distribution(df, 
                                                                                         feature_name, 
                                                                                         feature_name_top_colors)
    # Return new features names
    return [feature_name_binning, feature_name_binning_mode, feature_name_binning_dist,
            feature_name_top_colors, feature_name_top_colors_mode, feature_name_top_colors_dist
            ] + general_new_features
            