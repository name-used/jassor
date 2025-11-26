import importlib

my_modules = {
    'Reader': '.interface',
    'load': '.reader',
    'SingleDataset': '.single_predict_crop_dataset',
    'trans_norm': '.utils',
    'trans_linear': '.utils',
    'sample_image': '.utils',
    'sample_slide': '.utils',
    'AsapSlide': '.reader_asap',
    'OpenSlide': '.reader_openslide',
    'ImageSlide': '.reader_image',
    'NumpySlide': '.reader_numpy',
    'TiffSlide': '.reader_tiff',
    'crop': '.cropper',
}


def __getattr__(name):
    if name in my_modules:
        module = importlib.import_module(my_modules[name], __package__)
        return getattr(module, name)
    else:
        raise ModuleNotFoundError(f'The import name {name} not in this utils, check if want to import {list(my_modules.keys())}')


__all__ = list(my_modules)
