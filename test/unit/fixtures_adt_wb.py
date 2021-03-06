PREAUDIT_ACTIVATION_XML='''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/oo/classes/cl_hello_world" adtcore:name="CL_HELLO_WORLD"/>
</adtcore:objectReferences>'''

INACTIVE_OBJECTS_XML='''<?xml version="1.0" encoding="UTF-8"?>
<ioc:inactiveObjects xmlns:ioc="http://www.sap.com/abapxml/inactiveCtsObjects">
  <ioc:entry>
    <ioc:object/>
    <ioc:transport ioc:user="DEVELOPER" ioc:linked="false">
      <ioc:ref xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/C50K000377" adtcore:type="/RQ" adtcore:name="C50K000377" adtcore:description="Simply transport"/>
    </ioc:transport>
  </ioc:entry>
  <ioc:entry>
    <ioc:object ioc:user="" ioc:deleted="false">
      <ioc:ref xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/cl_hello_world" adtcore:type="CLAS/OC" adtcore:name="CL_HELLO_WORLD"/>
    </ioc:object>
    <ioc:transport/>
  </ioc:entry>
  <ioc:entry>
    <ioc:object ioc:user="" ioc:deleted="false">
      <ioc:ref xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/cl_hello_world/includes/definitions" adtcore:type="CLAS/OCN/definitions" adtcore:name="CL_HELLO_WORLD" adtcore:parentUri="/sap/bc/adt/oo/classes/cl_hello_world"/>
    </ioc:object>
    <ioc:transport ioc:user="DEVELOPER" ioc:linked="true">
      <ioc:ref xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/C50K000378" adtcore:type="/RQ" adtcore:name="C50K000378" adtcore:parentUri="/sap/bc/adt/vit/wb/object_type/%20%20%20%20rq/object_name/C50K000377" adtcore:description="Simply transport"/>
    </ioc:transport>
  </ioc:entry>
  <ioc:entry>
    <ioc:object ioc:user="" ioc:deleted="true">
      <ioc:ref xmlns:adtcore="http://www.sap.com/adt/core" adtcore:uri="/sap/bc/adt/oo/classes/cl_hello_world/includes/implementations" adtcore:type="CLAS/OCN/implementations" adtcore:name="CL_HELLO_WORLD" adtcore:parentUri="/sap/bc/adt/oo/classes/cl_hello_world"/>
    </ioc:object>
    <ioc:transport/>
  </ioc:entry>
</ioc:inactiveObjects>'''

ACTIVATION_REFERENCES_XML='''<?xml version="1.0" encoding="UTF-8"?>
<adtcore:objectReferences xmlns:adtcore="http://www.sap.com/adt/core">
<adtcore:objectReference adtcore:uri="/sap/bc/adt/oo/classes/cl_hello_world" adtcore:type="CLAS/OC" adtcore:name="CL_HELLO_WORLD"/>
<adtcore:objectReference adtcore:uri="/sap/bc/adt/oo/classes/cl_hello_world/includes/definitions" adtcore:type="CLAS/OCN/definitions" adtcore:name="CL_HELLO_WORLD" adtcore:parentUri="/sap/bc/adt/oo/classes/cl_hello_world"/>
</adtcore:objectReferences>'''

