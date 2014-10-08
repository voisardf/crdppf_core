<%inherit file="../base/index.mako"/>


% if debug:
    <!-- GENERAL LIBRARIES -->
    
    <!-- CUSTOM CRDPPF STUFF -->
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/resources/Fr.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/resources/De.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/formulaire.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/admintoolbar.js')}"></script>
% else:
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/formulaire.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/admintoolbar.js')}"></script>
% endif
    
    
<div id="tbar"></div>
<div id="main"></div>
