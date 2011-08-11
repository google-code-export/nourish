Ext.application({
  name: 'artistGrid',
  launch: function() {
  // wrapped in closure to prevent global vars.
  Ext.define('RegisteredGuests', {
      extend: 'Ext.data.Model',
      fields: ['id', 'name', 'url', 'invite', 'confirmed', 'admins', 'adminString']
  });

  var RegisteredGuestsStore = Ext.create('Ext.data.Store', {
      model: 'RegisteredGuests',
      sorters: ['name'],
      data: registeredGuests
  });

  var getGuestEmails = function() {
    getEmails(agsm);
  }

  var getHostEmails = function() {
      getEmails(tcsm);
  }

  var getUnconfirmedEmails = function() {
      getEmails(ucsm);
  }

  var agsm = Ext.create('Ext.selection.CheckboxModel', {
    checkOnly: true
  });

  var tcsm = Ext.create('Ext.selection.CheckboxModel', {
    checkOnly: true
  });

  var ucsm = Ext.create('Ext.selection.CheckboxModel', {
    checkOnly: true
  });

  var getEmails = function(selModel) {
    var emails = "";
    
    var selections = selModel.getSelection()
    for (var i = 0; i < selections.length; i++) {
      for (adminRecord in selections[i].data.admins) {
        emails += selections[i].data.admins[adminRecord].email + ', ';
      }
    }

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
      selModel: agsm,
      width: 950,
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
      columns: [Ext.create('Ext.grid.RowNumberer'),{
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
      },{
          text: 'Inv',
          width: 40,
          menuDisabled: true,
          dataIndex: 'invite'
      },{
          text: 'ConF',
          width: 40,
          menuDisabled: true,
          dataIndex: 'confirmed'
      }]
  });

  Ext.define('RegisteredHosts', {
      extend: 'Ext.data.Model',
      fields: ['id', 'name', 'url',  'invite', 'confirmed', 'admins', 'adminString']
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
      selModel: tcsm,
      width: 950,
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
      columns: [Ext.create('Ext.grid.RowNumberer'), {
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
      },{
          text: 'Inv',
          width: 40,
          menuDisabled: true,
          dataIndex: 'invite'
      },{
          text: 'ConF',
          width: 40,
          menuDisabled: true,
          dataIndex: 'confirmed'
      }]
  });

  Ext.define('UnconfirmedGuests', {
      extend: 'Ext.data.Model',
      fields: ['id', 'name', 'url', 'admins', 'adminString']
  });

  var UnconfirmedGuestsStore = Ext.create('Ext.data.Store', {
      model: 'UnconfirmedGuests',
      sorters: ['name'],
      data: unconfirmedGuests
  });
    
  var unconfirmedGuestsGrid = Ext.create('Ext.grid.Panel', {
      renderTo: 'unconfirmedGuests',
      frame: true,
      border: false,
      minHeight: 50,
      title: 'Artists Groups with Unconfirmed Invitations',
      store: UnconfirmedGuestsStore,
      selModel: ucsm,
      width: 950,
      features: [{
          ftype: 'summary'
      }],
      autoHeight: true,
      dockedItems: [{
        xtype: 'toolbar',
        items: [{
            text:'Get emails',
            tooltip:'retrieves a comma separated list of the emails for each group',
            handler: getUnconfirmedEmails
        }]
      }],
      viewConfig: {
        emptyText: "There are no artists groups with unconfirmed invitations.",
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
              return Ext.String.format('{0} Artist Group{1}', value, value !== 1 ? 's' : '');
          },
          tpl: '<a href="{url}"><span title="{name}">{name:ellipsis(45)}</span></a>'
      },{
          text: 'Contact',
          flex: 2,
          menuDisabled: true,
          dataIndex: 'adminString'
      }]
  });

  // MEAL CHART
  Ext.define('Artist', {
      extend: 'Ext.data.Model',
      fields: ['name', 'desc', 'date', 'dateFormat',
        'url', 'numPeople', 'invited', 'inviteGroup', 'adminString']
  });

  var ArtistStore = Ext.create('Ext.data.Store', {
      storeId: 'artists',
      model: 'Artist',
      sorters: [{property: 'invited', direction: 'ASC'}, {property: 'numPeople', direction: 'DESC'}, 'name'],
      groupField: 'dateFormat',
      data: meals
  });

  var groupingFeature = Ext.create('Ext.grid.feature.GroupingSummary',{
      groupHeaderTpl: '{name} ({rows.length} Artist Group{[values.rows.length > 1 ? "s" : ""]})'
  });

  var filterFn = function() {
    ArtistStore.clearFilter();
    ArtistStore.filter({
      filterFn: function(item) {
        var keep = false;
        if (newBox.getValue()) {
          keep = keep || (item.data.invited == "New");
        }
        if (inviteBox.getValue()) {
          keep = keep || (item.data.invited == "Invited");
        }
        if (confirmBox.getValue()) {
          keep = keep || (item.data.invited == "Confirmed");
        }
        return keep;
      }
    })
    grid.doLayout();
  }

  /**
   * Convenience function for creating filter configs for checkboxes
   * @param {Object} config Optional config object
   * @return {Object} The new Button configuration
   */
  function cfg(config) {
      config = config || {};
      Ext.applyIf(config, {
          listeners: {
              change: function(checkbox) {
                  filterFn();
              }
          },
          name: 'filter',
          checked: true
      });
      return config;
  }

  var newBox = Ext.create('Ext.form.field.Checkbox', cfg({boxLabel: 'New', inputValue: 'New'}));
  var inviteBox = Ext.create('Ext.form.field.Checkbox', cfg({boxLabel: 'Invited', inputValue: 'Invited'}));
  var confirmBox = Ext.create('Ext.form.field.Checkbox', cfg({boxLabel: 'Confirmed', inputValue: 'Confirmed'}));

  //create the toolbar with the 2 plugins
  var tbar = Ext.create('Ext.toolbar.Toolbar', {
      items : [{
            xtype: 'tbtext',
            text: 'Filtering:'
        },
        newBox,
        inviteBox,
        confirmBox
      ]
  });
    
  var grid = Ext.create('Ext.grid.Panel', {
      renderTo: 'meals',
      frame: true,
      title: "All Meals",
      border: false,
      minHeight: 50,
      tbar: tbar,
      store: ArtistStore,
      //selModel: sm,
      width: 1400,
      autoHeight: true,
      viewConfig: {
        getRowClass: function(record, rowIndex, rowParams, store){
          if(record.get("invited").match("New") != null) {
            return "newRow";
          } else if (record.get("invited").match("Invited") != null) {
            return "pendingRow";
          } else if (record.get("invited").match("Confirmed") != null) {
            return "confirmedRow";
          }

          return "";
        },
        minHeight: 50
      },
      features: [groupingFeature],
      columns: [{
          text: 'Artist Group',
          flex: 2,
          tdCls: 'artistNameColumn',
          menuDisabled: true,
          dataIndex: 'name',
          xtype: 'templatecolumn',
          tpl: '<a href="{url}"><span title="{name}">{name:ellipsis(45)}</span></a>',
          summaryType: 'count',
          summaryRenderer: function(value, summaryData, dataIndex) {
            return ((value === 0 || value > 1) ? '(' + value + ' Dinners)' : '(1 Dinner)');
          }
      },{
          text: 'Members',
          flex: 0,
          width: 58,
          menuDisabled: true,
          dataIndex: 'numPeople',
          summaryType: 'sum',
          summaryRenderer: function(value, summaryData, dataIndex) {
              return value + ' Total';
          },
          field: { xtype: 'numberfield' }
      },{
          text: 'Artist Contact',
          flex: 2,
          menuDisabled: true,
          dataIndex: 'guestMealAdminString'
      },{
          text: 'Invitation Status',
          flex: 1,
          menuDisabled: true,
          dataIndex: 'invited',
          xtype: 'templatecolumn',
          tpl: '{invited}'
      },{
          text: 'Theme Camp Group',
          flex: 1,
          menuDisabled: true,
          dataIndex: 'invited',
          xtype: 'templatecolumn',
          tpl: '{inviteGroup}'
      },{
          text: 'Theme Camp Contact',
          flex: 2,
          menuDisabled: true,
          dataIndex: 'hostMealAdminString'
      },{
          text: 'Address',
          flex: 1,
          menuDisabled: true,
          dataIndex: 'address'
      },{
          text: 'Dinner Time',
          flex: 1,
          menuDisabled: true,
          dataIndex: 'dinnerTime'
      }]
  });
}});
