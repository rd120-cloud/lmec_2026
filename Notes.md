# June 3
Housing as a verb instead of a noun. [Key theme of the summer]

https://climateandcommunity.org/ - Check these guys out for cool climate research!

## Links to investigate
Here are some of the publications I looked at today to familiarize myself with the style and content LMEC is interested in.
- https://www.leventhalmap.org/articles/dating-every-building-in-boston/
    - This one was actually very straightforward. I'm already really familiar with housing assessment data (see EC204 Trees paper). This also seems like a pretty basic suite of visualizations, which could inform how much effort I put into that for my project.
- https://www.leventhalmap.org/articles/making-water-into-gold/
    - Pretty cool premise, I knew a bit about this history but it was good to learn more. I appreciate the political dimension that Garrett added here, good thing to consider. This type of analysis definitely aligns with my goals.
    - https://www.kaggle.com/code/garrettdashnelson/underwater-properties - This is the code that goes with the report
- https://www.leventhalmap.org/digital-exhibitions/getting-around-town/
    - This was the first exhibit I looked at. Super interesting combos of historic maps and historic photographs and documents, paints a really quotidian picture of what transit was like in the past in Boston. Also, I'm starting to get a good sense of the narrative construction of the exhibits, might be valuable to inform my work. I should assemble a data set that can be easily slotted into a narrative.
    - I think its also interesting how this exhibit specifically locates the historic developments using features of the city that people know right now. I guess it's obvious for a mapping exhibit, but I think it's good to keep in mind as well for my work because I want to make sure that when people use my data set it can be easily incorporated into the exhibit with straightforward location references. I should include neighborhood or location categories for data, even if most of the relevant indexing will be geohashed or whatever.
- https://www.leventhalmap.org/digital-exhibitions/processing-place/
    - This was an awesome exhibit. This exhibit should be the intro section to a GIS class, big fan. The visual style is also incredibly appealing. Genuinely great piece of education and art.
- http://leventhalmap.org/digital-exhibitions/declarations/
    - Current exhibit.
    - I'm getting a sense now for the repeated visual style of a lot of these exhibits. Square rendering of a valuable, representative, or interesting document, and then side column of text. 
- https://www.leventhalmap.org/digital-exhibitions/bending-lines/#content
- https://www.leventhalmap.org/digital-exhibitions/more-or-less-in-common/
- https://www.leventhalmap.org/digital-exhibitions/building-blocks/
- https://www.leventhalmap.org/articles/section-112-in-the-boston-region-universities-hospitals-and-urban-renewal/
    - Grant funded project I looked at.
- https://mappinghny.com/
    - Example of micro data, at the level of individual people. Could be relevant to frame my use of micro data.
- https://housing-submarkets.mapc.org/
    - This is a reference for a possible project I could pursue. Replicate this analysis for historic Boston.
- https://osf.io/preprints/socarxiv/5w6jx_v1

## Ideas I can pursue as my project
- Do housing submarkets but historically
  - Reach out to MAPC people to see what methods they used to make these maps
- Zoning and regulation impact on housing over time?
- Track the movement of individuals over time to see the dynamics of moving in the city
  - Create digraphs with geohashed nodes and distance weights on edges mapping changes in housing of a certain individual from one location to another
- Demography with micro data?
  - Maybe look at large periods of immigration or development
  - Look at "inflection points" in housing use demographics
- Something about urban green space access?
  - I already have a lot of experience and data in this regard
  - Create a valuable data set of historic land use in the region. Does this data already exist?

What will these types of projects look like, in terms of what type of work I can do with the materials at the LMEC? Probably will rely on much recompilation, because I am already really familiar with Analyze Boston data, IPUMs, etc. I think working with historic maps would be really valuable to track housing, parcelization, and land use, which could provide an opportunity for digitization.

Things to look into:
- ML methods for geocoding parcel polygons from scanned maps?

# June 4

Primary output is a really thorough and reusable dataset.

Criteria for the dataset project:
- Uses LMEC and BPL collection objects.
  - Ideally animates resources already in collections with supplemental data or analysis.
  - I.e. digitized and compiled data from collection maps
- Reproducible and extensible
  - Can be extended temporally and spatially
  - Notebook and code and whatnot
- Data is published in plaintext open formats

## Data Availability Investigation
Zoning maps:
- GW Bromley and Co. Atlas of Boston
  - 1883/1884
  - 1902
  - 1938
- Boston City Planning Comission, 1924, https://www.digitalcommonwealth.org/search/commonwealth:7h14cv727/manifest
  - This is the first official planning map for the city with a regulatory zoning policy attatched
- Boston Zoning Commission, 1962, only maps available online are downtown/bb, Eastie, JP
  - https://www.digitalcommonwealth.org/search?f%5Bname_facet_ssim%5D%5B%5D=Boston+Zoning+Commission 
- Urban renewal proposed zoning maps, ~1965
- BRA 

General timeline may look like pre 1870 (before acquiring Dorchester, Mattapan, Roxbury, Brighton, etc., which happened between 1864 and 1870), 1870-1914 (pre planning board), 1914-1957 (City Planning Board), 1957-1971 (Early BRA), 1971-1994 (Mid BRA, pre EDIC merger), 1994-2016 (Late BRA), 2016-present (BRA transition to BPD).

Because of the nature of sources, it may be practical to combine the green space analysis and the submarket analysis. This could be done using the housing assessments, zoning stats, and then general geospatial analysis.

What would be required would be a digitization of parcel maps with some enrichment using information about the parcels, maybe ownership and residency data, land use qualifications. Maybe some transit system mapping? Figure out way to divide blocks into parcels? Bromley maps are not uniformly georeferenced, so that will be a task.

Might be interesting to compare old "urban wilds" map and stylization to current urban wilds program? https://www.digitalcommonwealth.org/search/commonwealth:7h14cw341 

## Mid day update
I think I've decided I'm not going to pursue the idea about tracking where people are moving, because it's looking not very practical and the data is not super accessible just on a cursory look. Right now, I am leaning towards my dataset being a set of snapshot parcel maps and jurisdiction maps from 5-10 key "eras" in the city's history, which could be used to pursue the zoning changes idea, green space access, and submarkets depending on what I want to specialize into.

## Exploring methods
This AI vectorizing tool looks promising - https://www.geographyrealm.com/ai-digitize-data-scanned-maps/

# June 10
Digitizing methods to explore:
- Arc Detect Objects ML workflow
- GDAL preprocessing with a raster analysis framework
- 