# -*- coding: utf-8 -*-
from server.bones import baseBone
from math import pow, floor, ceil
from server import db
import logging
from math import sqrt
from random import random, sample, shuffle
from itertools import chain

class randomSliceBone( baseBone ):
	"""
		Holds numeric values.
		Can be used for ints and floats.
		For floats, the precision can be specified in decimal-places.
	"""

	type = "randomslice"

	def __init__(self, *args,  **kwargs ):
		"""
			Initializes a new randomSliceBone.

			:param precision: How may decimal places should be saved. Zero casts the value to int instead of float.
			:type precision: int
			:param min: Minimum accepted value (including).
			:type min: float
			:param max: Maximum accepted value (including).
			:type max: float
		"""
		baseBone.__init__( self, indexed=True, visible=False, readOnly=True,  *args,  **kwargs )
		self.boundsLat = (50.0,60.0)
		self.boundsLng = (10.0,20.0)
		self.gridDimensions = 10.0,12.0

	def serialize( self, name, entity ):
		"""
			Serializes this bone into something we
			can write into the datastore.

			:param name: The property-name this bone has in its Skeleton (not the description!)
			:type name: String
			:returns: dict
		"""
		entity.set(name, random(), True)
		return entity

	def buildDBSort( self, name, skel, dbFilter, rawFilter ):
		"""
			Same as buildDBFilter, but this time its not about filtering
			the results, but by sorting them.
			Again: rawFilter is controlled by the client, so you *must* expect and safely handle
			malformed data!

			:param name: The property-name this bone has in its Skeleton (not the description!)
			:type name: str
			:param skel: The :class:`server.skeleton.Skeleton` instance this bone is part of
			:type skel: :class:`server.skeleton.Skeleton`
			:param dbFilter: The current :class:`server.db.Query` instance the filters should be applied to
			:type dbFilter: :class:`server.db.Query`
			:param rawFilter: The dictionary of filters the client wants to have applied
			:type rawFilter: dict
			:returns: The modified :class:`server.db.Query`
		"""
		def applyFilterHook(dbfilter, property, value):
			"""
				Applies dbfilter._filterHook to the given filter if set,
				else return the unmodified filter.
				Allows orderby=random also be used in relational-queries.

			:param dbfilter:
			:param property:
			:param value:
			:return:
			"""
			if dbFilter._filterHook is None:
				return property, value
			try:
				property, value = dbFilter._filterHook(dbFilter, property, value)
			except:
				# Either, the filterHook tried to do something special to dbFilter (which won't)
				# work as we are currently rewriting the core part of it) or it thinks that the query
				# is unsatisfiable (fe. because of a missing ref/parent key in relationalBone).
				# In each case we kill the query here - making it to return no results
				raise RuntimeError()
			return property, value

		if "orderby" in list(rawFilter.keys()) and rawFilter["orderby"] == name:
			# We select a random set of elements from that collection
			assert not isinstance(dbFilter.datastoreQuery, db.MultiQuery), "Orderby random is not possible on a query that already uses an IN-filter!"
			origFilter = dbFilter.datastoreQuery
			origKind = dbFilter.getKind()
			queries = []
			for unused in range(0,3): #Fetch 3 Slices from the set
				rndVal = random() # Choose our Slice center
				# Right Side
				q = db.DatastoreQuery( kind=origKind )
				property, value = applyFilterHook(dbFilter, "%s <=" % name, rndVal)
				q[property] = value
				q.Order( (name, db.DESCENDING) )
				queries.append( q )
				# Left Side
				q = db.DatastoreQuery( kind=origKind )
				property, value = applyFilterHook(dbFilter, "%s >" % name, rndVal)
				q[property] = value
				queries.append( q )
			dbFilter.datastoreQuery = db.MultiQuery(queries, None)
			# Map the original filter back in
			for k, v in origFilter.items():
				dbFilter.datastoreQuery[ k ] = v
			dbFilter._customMultiQueryMerge = self.customMultiQueryMerge
			dbFilter._calculateInternalMultiQueryAmount = self.calculateInternalMultiQueryAmount
			logging.error("XXXX!")

	def calculateInternalMultiQueryAmount(self, targetAmount):
		return int(targetAmount/2)

	#(self, res, origLimit
	def customMultiQueryMerge(self, dbFilter, result, targetAmount):
		# res is a list of iterators at this point, chain them together
		res = chain(*[list(x) for x in result])
		# Remove duplicates
		tmpDict = {}
		for item in res:
			tmpDict[ str(item.key()) ] = item
		res = list(tmpDict.values())
		# Slice the requested amount of results our 3times lager set
		res = sample(res, min(len(res), targetAmount))
		shuffle(res)
		return res
