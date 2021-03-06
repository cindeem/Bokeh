import os
import re
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


_basedir = os.path.dirname(__file__)
demo_dir = os.path.join(_basedir, "../bokeh/server/static/demos")
GALLERY_SNIPPET_PATH = os.path.join(_basedir, "../sphinx/_templates/gallery_core.html")
#These settings work with localhost:5006
HOSTED_STATIC_ROOT="/static/"
DETAIL_URL_ROOT="/static/demos/detail/"
detail_dir = os.path.join(demo_dir, "detail")

def page_desc(prev_infos, module_desc):
    module_path, name_ = module_desc['file'], module_desc['name']
    varname= module_desc.get("varname", 'curplot')
    temp_dict = {}
    execfile(module_path, temp_dict)
    if varname=='curplot':
        plot = temp_dict[varname]()
    else:
        plot = temp_dict[varname]

    if len(prev_infos) > 0:
        prev_info = prev_infos[-1]
    else:
        prev_info = {}
    embed_snippet = plot.inject_snippet(
        embed_save_loc= detail_dir, static_path=HOSTED_STATIC_ROOT,
        embed_base_url=DETAIL_URL_ROOT)
    detail_snippet = highlight(open(module_path).read(), PythonLexer(), HtmlFormatter())
    page_info = dict(
        name=name_, embed_snippet=embed_snippet,
        detail_snippet = detail_snippet,
        detail_page_url=DETAIL_URL_ROOT + name_ + ".html",
        prev_detail_url=prev_info.get('detail_page_url', ""),
        prev_detail_name=prev_info.get('name', ""))
    if len(prev_infos) == 0:
        prev_infos = [page_info]
    else:
        prev_infos.append(page_info)

    return prev_infos

def _load_template(filename):
    import jinja2
    with open(os.path.join(_basedir, filename)) as f:
        return jinja2.Template(f.read())

def make_gallery(module_descs):
    page_infos = reduce(page_desc, module_descs, [])
    for p, p_next in [[p, page_infos[i+1]] for i, p in enumerate(page_infos[:-1])]:
        p['next_detail_url'] = p_next['detail_page_url']
        p['next_detail_name'] = p_next['name']
    t = _load_template("detail.html")    
    gallery_template = '''
    <li>
        <a href="%(detail_page_url)s">%(name)s
          <img src="/static/img/gallery/%(name)s.png"
               class="gallery" />
        </a>
        </li>
    '''
    gallery_snippet = '<ul class="gallery clearfix">'
    for info in page_infos:
        gallery_snippet +=  gallery_template % info

        fname = os.path.join(detail_dir, info['name'] + ".html")
        info['HOSTED_STATIC_ROOT']= HOSTED_STATIC_ROOT
        print " writing to ", fname
        with open(fname, "w") as f:
            f.write(t.render(info))
    gallery_snippet += "</ul>"    
    with open(GALLERY_SNIPPET_PATH, "w") as f:
        f.write(gallery_snippet)

if __name__ == "__main__":
    make_gallery(
        [
        dict(file="plotting/file/iris.py", name='iris',),    
        dict(file="plotting/file/candlestick.py", name='candlestick',),    
        dict(file="plotting/file/legend.py", name= 'legend',),    
        dict(file="plotting/file/correlation.py", name='correlation',),    
        dict(file="plotting/file/glucose.py", name= 'glucose',),    
        dict(file="plotting/file/stocks.py", name= 'stocks',),    
        dict(file="plotting/file/vector.py", name= 'vector_example',),    
        dict(file="plotting/file/lorenz.py", name= 'lorenz_example',),    
        dict(file="plotting/file/color_scatter.py", name= 'color_scatter_example',),    
        dict(file="glyphs/iris_splom.py", name='anscombe', varname="grid"),
        dict(file="glyphs/anscombe.py", name='anscombe', varname="grid"),
        dict(file="plotting/file/choropleth.py", name= 'choropleth_example',),    
        dict(file="plotting/file/texas.py", name= 'texas_example',),    
        dict(file="plotting/file/markers.py", name= 'scatter_example',),    
         ]
    )
    try:
        import webbrowser
        webbrowser.open(HOSTED_STATIC_ROOT + "demos/gallery.html")
    except:
        pass
