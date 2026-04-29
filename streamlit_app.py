import streamlit as st
import json
import uuid

# --- Page Configuration ---
st.set_page_config(layout="wide", page_title="Perkins Integration Toolkit")

# --- Data Dictionaries for Conditional Logic ---
FUNCTIONS = [
    'addLead', 'addContact', 'addCampaignMember', 
    'addToPublicationList', 'addToPublicationListV2', 
    'addOrganizationAccount', 'addTask'
]

TARGET_MAPS = {
    'addLead': ['FirstName', 'LastName', 'Email', 'Street', 'City', 'StateCode', 'CountryCode', 'PostalCode', 'Company', 'LeadSource', 'Lead_Source_Detail__c'],
    'addContact': ['FirstName', 'LastName', 'Email', 'MailingStreet', 'MailingCity', 'MailingStateCode', 'MailingCountryCode', 'MailingPostalCode', 'LeadSource', 'Con_SrcDtl__c', 'AccountId', 'RecordType'],
    'addCampaignMember': ['CampaignId', 'LeadId', 'ContactId', 'Status'],
    'addToPublicationList': ['LeadId', 'ContactId', 'Campaign__c', 'Publication_List__c', '_optIn'],
    'addToPublicationListV2': ['LeadId', 'ContactId', 'Campaign__c', 'Publication_List__c', '_optIn'],
    'addOrganizationAccount': ['Name', 'BillingStreet', 'BillingCity', 'BillingStateCode', 'BillingPostalCode', 'BillingCountryCode', 'ShippingStreet', 'ShippingCity', 'ShippingStateCode', 'ShippingPostalCode', 'ShippingCountryCode', 'ContactId', 'npe5__Role__c'],
    'addTask': ['Subject', 'Description', 'ContactId', 'LeadId', 'WhatId', 'Status', 'RecordType', 'Campaign__c']
}

FORMATS = ['None', 'concatenate', 'datetime']
OPTION_TYPES = ['addToPublicationListByCampaign', 'addToPublicationListByListId', 'addCampaignMember', 'addOrganizationAccount']

# --- State Management ---
def init_state():
    if 'steps' not in st.session_state:
        st.session_state.steps = [{
            'id': str(uuid.uuid4()),
            'name': 'step1',
            'function': 'addLead',
            'environment': 're',
            'options': [],
            'maps': [{
                'id': str(uuid.uuid4()), 
                'source': '', 
                'target': 'FirstName', 
                'format': 'None', 
                'value': '', 
                'path': ''
            }]
        }]

init_state()

# --- State Mutation Callbacks ---
def add_step():
    st.session_state.steps.append({
        'id': str(uuid.uuid4()),
        'name': f'step{len(st.session_state.steps) + 1}',
        'function': 'addLead',
        'environment': 're',
        'options': [],
        'maps': []
    })

def remove_step(step_id):
    st.session_state.steps = [s for s in st.session_state.steps if s['id'] != step_id]

def add_option(step_id):
    for s in st.session_state.steps:
        if s['id'] == step_id:
            s['options'].append({
                'id': str(uuid.uuid4()), 
                'option': OPTION_TYPES[0], 
                'value': ''
            })

def remove_option(step_id, option_id):
    for s in st.session_state.steps:
        if s['id'] == step_id:
            s['options'] = [o for o in s['options'] if o['id'] != option_id]

def add_map(step_id):
    for s in st.session_state.steps:
        if s['id'] == step_id:
            s['maps'].append({
                'id': str(uuid.uuid4()), 
                'source': '', 
                'target': TARGET_MAPS[s['function']][0] if TARGET_MAPS.get(s['function']) else '', 
                'format': 'None', 
                'value': '', 
                'path': ''
            })

def remove_map(step_id, map_id):
    for s in st.session_state.steps:
        if s['id'] == step_id:
            s['maps'] = [m for m in s['maps'] if m['id'] != map_id]

# --- JSON Generation ---
def generate_json():
    clean_steps = []
    for s in st.session_state.steps:
        step_obj = {
            "name": s['name'],
            "function": s['function'],
            "environment": s['environment']
        }
        
        # Clean Options
        clean_options = []
        for o in s['options']:
            if o['option'] or o['value']:
                clean_options.append({"option": o['option'], "value": o['value']})
        if clean_options:
            step_obj["options"] = clean_options
            
        # Clean Maps
        clean_maps = []
        for m in s['maps']:
            m_obj = {}
            if m['source']: m_obj['source'] = m['source']
            if m['target']: m_obj['target'] = m['target']
            if m['format'] and m['format'] != 'None': m_obj['format'] = m['format']
            if m['value']: m_obj['value'] = m['value']
            if m['path']: m_obj['path'] = m['path']
            
            if m_obj:
                clean_maps.append(m_obj)
                
        if clean_maps:
            step_obj["map"] = clean_maps
            
        clean_steps.append(step_obj)
        
    return json.dumps({"process": {"step": clean_steps}}, indent=2)

# --- Main UI Layout ---
st.title("🗄️ Perkins Integration Toolkit")
st.caption("Configure your automated processes and data mappings.")

# Create a split layout mimicking the React app
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.subheader("Form Builder")
    
    for i, step in enumerate(st.session_state.steps):
        with st.container(border=True):
            cols_header = st.columns([10, 1])
            cols_header[0].markdown(f"**Step {i+1}: {step['name'] or 'Unnamed'}**")
            if cols_header[1].button("🗑️", key=f"del_step_{step['id']}", help="Remove Step"):
                remove_step(step['id'])
                st.rerun()

            # Step Fundamentals
            sc1, sc2, sc3 = st.columns(3)
            step['name'] = sc1.text_input("Step Name (Unique)", value=step['name'], key=f"name_{step['id']}")
            
            # Update targets dynamically based on function selection
            old_func = step['function']
            step['function'] = sc2.selectbox("Process Function", FUNCTIONS, index=FUNCTIONS.index(step['function']), key=f"func_{step['id']}")
            
            # If function changed, reset targets in existing maps to prevent invalid states
            if old_func != step['function']:
                default_target = TARGET_MAPS[step['function']][0] if TARGET_MAPS.get(step['function']) else ""
                for m in step['maps']:
                    m['target'] = default_target

            step['environment'] = sc3.text_input("Environment", value=step['environment'], key=f"env_{step['id']}")

            st.divider()

            # Options Section
            opt_cols = st.columns([8, 2])
            opt_cols[0].markdown("##### ⚙️ Options")
            if opt_cols[1].button("➕ Add Option", key=f"add_opt_{step['id']}"):
                add_option(step['id'])
                st.rerun()

            if not step['options']:
                st.caption("No options configured.")
                
            for opt in step['options']:
                with st.container(border=True):
                    oc1, oc2, oc3 = st.columns([4, 4, 1])
                    opt['option'] = oc1.selectbox("Option Type", OPTION_TYPES, index=OPTION_TYPES.index(opt['option']), key=f"opttype_{opt['id']}")
                    opt['value'] = oc2.text_input("Value", value=opt['value'], key=f"optval_{opt['id']}")
                    if oc3.button("🗑️", key=f"del_opt_{opt['id']}"):
                        remove_option(step['id'], opt['id'])
                        st.rerun()

            st.divider()

            # Maps Section
            map_cols = st.columns([8, 2])
            map_cols[0].markdown("##### 🔀 Data Mappings")
            if map_cols[1].button("➕ Add Map", key=f"add_map_{step['id']}"):
                add_map(step['id'])
                st.rerun()

            for m in step['maps']:
                with st.container(border=True):
                    # Delete Map Button
                    if st.button("🗑️ Remove Map", key=f"del_map_{m['id']}", type="tertiary"):
                        remove_map(step['id'], m['id'])
                        st.rerun()

                    mc1, mc2, mc3, mc4 = st.columns(4)
                    
                    # Target dropdown (depends on selected step function)
                    available_targets = TARGET_MAPS.get(step['function'], ["Custom..."])
                    current_target = m['target'] if m['target'] in available_targets else available_targets[0]
                    m['target'] = mc1.selectbox("Target Field", available_targets, index=available_targets.index(current_target), key=f"maptgt_{m['id']}")
                    
                    # Source vs Value Logic (Disable one if the other is filled)
                    has_value = bool(m['value'])
                    has_source = bool(m['source'])
                    
                    m['source'] = mc2.text_input("Source (Jotform)", value=m['source'], disabled=has_value, key=f"mapsrc_{m['id']}")
                    m['value'] = mc3.text_input("Constant Value", value=m['value'], disabled=has_source, key=f"mapval_{m['id']}", help="Overrides Source")
                    
                    # Format
                    m['format'] = mc4.selectbox("Format", FORMATS, index=FORMATS.index(m['format']), key=f"mapfmt_{m['id']}")
                    
                    # Path
                    m['path'] = st.text_input("Previous Step Path Reference (Advanced)", value=m['path'], key=f"mappath_{m['id']}", placeholder="e.g. /process/package/path")

    # Add Step Button
    if st.button("➕ Add Another Step", use_container_width=True, type="primary"):
        add_step()
        st.rerun()

# --- Live JSON Preview ---
with col_right:
    st.subheader("JSON Output")
    st.caption("Ready for JotForms / Form Assembly. Hover over the code block to copy.")
    
    # Generate live JSON based on current state
    output_json = generate_json()
    st.code(output_json, language="json")
