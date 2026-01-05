import importlib
my_modules = {
    'Logger': '.logger',
    'TimerManager': '.timer',
    'Timer': '.timer',
    'Queue': '.multiprocess',
    'Closed': '.multiprocess',
    'Process': '.multiprocess',
    'QueueMessageException': '.multiprocess',
    'JassorJsonEncoder': '.json_encoder',
    'Merger': '.merger',
    'random_colors': '.color',
    'random_rainbow_curves': '.color',
    'plot': '.jassor_plot_lib',
    'plots': '.jassor_plot_lib',
    'Table': '.table',
    'uniform_iter': '.iter_method',
    'crop': '.cropper',
    # 'SlideWriter': '.writer_asap',
    'SlideWriter': '.writer_tifffile',
    'image2slide': '.writer_tiff',
    'BBox': '.bbox',
    'bbox_to_contour': '.bbox',
    'bbox_join_region': '.bbox',
    'bbox_inter': '.bbox',
    'bbox_inter_area_matrix': '.bbox',
    'bbox_lurd2xywh': '.bbox',
    'bbox_xywh2lurd': '.bbox',
    'bbox_luwh2xywh': '.bbox',
    'bbox_xywh2luwh': '.bbox',
    'bbox_lurd2luwh': '.bbox',
    'bbox_luwh2lurd': '.bbox',
    'ipynb2pycode': '.ipynb2pycode',
    'find_contour': '.contour',
    'geojson2shapes': '.contour',
    'align_fourier': '.align_in_fourier',
    'align_keypoint': '.align_in_keypoint',
}


def __getattr__(name):
    if name in my_modules:
        module = importlib.import_module(my_modules[name], __package__)
        return getattr(module, name)
    else:
        raise ModuleNotFoundError(f'The import name {name} not in this utils, check if want to import {list(my_modules.keys())}')


__all__ = list(my_modules)
