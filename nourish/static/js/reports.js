Ext.application({
  name: 'artistGrid',
  launch: function() {
  // wrapped in closure to prevent global vars.
  Ext.define('RegisteredGuests', {
      extend: 'Ext.data.Model',
      fields: ['id', 'name', 'url', 'admins', 'adminString']
  });

  var RegisteredGuestsStore = Ext.create('Ext.data.Store', {
      model: 'RegisteredGuests',
      sorters: ['name'],
      data: registeredGuests
  });

  var getGuestEmails = function() {
    getEmails(RegisteredGuestsStore);
  }

  var getHostEmails = function() {
      getEmails(RegisteredHostsStore);
  }

  var getEmails = function(store) {
    var emails = "";
    store.each(function(record) {
      var admins = record.get("admins");
      for (adminRecord in admins) {
        emails += admins[adminRecord].email + ', ';
      }
    });

    Ext.create('Ext.Window', {
        title: 'Copy emails addresses below',
        width: 400,
        height: 200,
        layout: 'fit',
        items: {
            xtype: 'textarea',
            value: emails,
            anchor: '100%'
        }
    }).show();
  }

  var guestGrid = Ext.create('Ext.grid.Panel', {
      renderTo: 'registeredGuests',
      frame: true,
      border: false,
      minHeight: 50,
      title: 'Registered Artists',
      store: RegisteredGuestsStore,
      //selModel: sm,
      width: 775,
      dockedItems: [{
        xtype: 'toolbar',
        items: [{
            text:'Get emails',
            tooltip:'retrieves a comma separated list of the emails for each group',
            handler: getGuestEmails
        }]
      }],
      autoHeight: true,
      viewConfig: {
        emptyText: "There are no Artists currently registered for this event.",
        minHeight: 50
      },
      features: [{
          ftype: 'summary'
      }],
      columns: [{
          text: 'Name',
          flex: 1,
          menuDisabled: true,
          dataIndex: 'name',
          xtype: 'templatecolumn',
          summaryType: 'count',
          summaryRenderer: function(value, summaryData, dataIndex) {
              return Ext.String.format('{0} Artist{1}', value, value !== 1 ? 's' : '');
          },
          tpl: '<a href="{url}"><span title="{name}">{name:ellipsis(45)}</span></a>'
      },{
          text: 'Contact',
          flex: 2,
          menuDisabled: true,
          dataIndex: 'adminString'
      }]
  });

  Ext.define('RegisteredHosts', {
      extend: 'Ext.data.Model',
      fields: ['id', 'name', 'url', 'admins', 'adminString']
  });

  var RegisteredHostsStore = Ext.create('Ext.data.Store', {
      model: 'RegisteredHosts',
      sorters: ['name'],
      data: registeredHosts
  });
    
  var hostGrid = Ext.create('Ext.grid.Panel', {
      renderTo: 'registeredHosts',
      frame: true,
      border: false,
      minHeight: 50,
      title: 'Registered Theme Camps',
      store: RegisteredHostsStore,
      //selModel: sm,
      width: 775,
      features: [{
          ftype: 'summary'
      }],
      autoHeight: true,
      dockedItems: [{
        xtype: 'toolbar',
        items: [{
            text:'Get emails',
            tooltip:'retrieves a comma separated list of the emails for each group',
            handler: getHostEmails
        }]
      }],
      viewConfig: {
        emptyText: "There are no Theme Camps currently registered for this event.",
        minHeight: 50
      },
      columns: [{
          text: 'Name',
          flex: 1,
          menuDisabled: true,
          dataIndex: 'name',
          xtype: 'templatecolumn',
          summaryType: 'count',
          summaryRenderer: function(value, summaryData, dataIndex) {
              return Ext.String.format('{0} Theme Camp{1}', value, value !== 1 ? 's' : '');
          },
          tpl: '<a href="{url}"><span title="{name}">{name:ellipsis(45)}</span></a>'
      },{
          text: 'Contact',
          flex: 2,
          menuDisabled: true,
          dataIndex: 'adminString'
      }]
  });
}});
