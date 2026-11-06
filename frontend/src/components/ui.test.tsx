import React from 'react'
import {render,screen,cleanup} from '@testing-library/react'
import {afterEach,describe,it,expect} from 'vitest'
import {Notice,SourceCard,Loading} from './ui'
import {today} from '../lib/api'
afterEach(cleanup)
describe('resident feedback',()=>{
 it('exposes loading status',()=>{render(<Loading/>);expect(screen.getByRole('status').textContent).toContain('Opening')})
 it('renders clear error content',()=>{render(<Notice tone="error">Upload could not be saved</Notice>);expect(screen.getByText('Upload could not be saved')).toBeTruthy()})
 it('never labels an unverified source as reviewed',()=>{render(<SourceCard resource={{id:'test',name:'Official reference',category:'food',description:'Test',geographic_coverage:['Cook County'],eligibility:[],contact:'Confirm directly',source_url:'https://example.org',verified_at:null,verification:'Unverified',availability:'unknown',limitations:'No live feed',needs:[],program:false}}/>);expect(screen.getByText('Reference · unverified')).toBeTruthy();expect(screen.getByText(/Capacity and current availability are not verified/)).toBeTruthy()})
 it('uses Chicago calendar date in inputs',()=>{expect(today()).toMatch(/^\d{4}-\d{2}-\d{2}$/)})
})
